import time
import json
import ssl
import socket
import subprocess
import logging
from concurrent.futures import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import SessionLocal
from models import HostDB, PingResultDB, SpeedTestResultDB, PublicIPHistoryDB
from ping3 import ping
from datetime import timedelta, datetime
from urllib.parse import urlparse
import requests

from notifications import notification_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
_speedtest_executor = ThreadPoolExecutor(max_workers=1)
_speedtest_running = False


def check_public_ip():
    db = SessionLocal()
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=10)
        if response.status_code == 200:
            ip_address = response.json().get("ip")
            last_record = db.query(PublicIPHistoryDB).order_by(PublicIPHistoryDB.timestamp.desc()).first()
            last_ip = last_record.ip_address if last_record else None
            if last_ip != ip_address:
                logger.info(f"Public IP changed: {last_ip} → {ip_address}")
                db.add(PublicIPHistoryDB(ip_address=ip_address))
                db.commit()
        else:
            logger.error(f"Failed to get public IP: {response.status_code}")
    except Exception as e:
        logger.error(f"Error checking public IP: {e}")
    finally:
        db.close()


def _run_speedtest_sync():
    """Runs in a separate thread via ThreadPoolExecutor to avoid blocking the scheduler."""
    global _speedtest_running
    if _speedtest_running:
        logger.info("Speedtest already running, skipping.")
        return
    _speedtest_running = True
    db = SessionLocal()
    try:
        logger.info("Starting Internet Speed Test...")
        cmd = ["speedtest-cli", "--json", "--secure"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            logger.error(f"Speedtest failed: {result.stderr}")
            return
        data = json.loads(result.stdout)
        download_mbps = data["download"] / 1_000_000
        upload_mbps = data["upload"] / 1_000_000
        ping_ms = data["ping"]
        logger.info(f"Speedtest: D:{download_mbps:.2f} Mbps U:{upload_mbps:.2f} Mbps P:{ping_ms:.2f}ms")
        db.add(SpeedTestResultDB(
            download=download_mbps,
            upload=upload_mbps,
            ping=ping_ms,
            server_id=data["server"]["id"],
            server_name=data["server"]["name"],
            server_country=data["server"]["country"],
        ))
        db.commit()
    except Exception as e:
        logger.error(f"Error running speedtest: {e}")
    finally:
        _speedtest_running = False
        db.close()


def run_speedtest():
    """Submit speedtest to dedicated thread pool — never blocks the scheduler."""
    _speedtest_executor.submit(_run_speedtest_sync)


def check_http(url: str, expected_status: int = 200, timeout: int = 5):
    try:
        if not url.startswith("http"):
            url = f"http://{url}"
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        latency = (time.time() - start_time) * 1000
        is_up = response.status_code == expected_status
        return is_up, latency, response.status_code
    except Exception as e:
        logger.warning(f"HTTP check failed for {url}: {e}")
        return False, -1.0, 0


def check_ssl_job():
    logger.info("Starting SSL Certificate Check Job...")
    db: Session = SessionLocal()
    try:
        hosts = db.query(HostDB).filter(HostDB.ssl_monitor == True, HostDB.enabled == True).all()
        for host in hosts:
            try:
                target_host = host.ip_address
                if target_host.startswith("http"):
                    parsed = urlparse(target_host)
                    target_host = parsed.netloc.split(":")[0]
                days_remaining = check_ssl_expiry(target_host, host.port or 443)
                if days_remaining is not None:
                    host.ssl_expiry_days = days_remaining
                    host.ssl_error = None
                    alert_days = [30, 14, 7, 3, 1]
                    if days_remaining in alert_days or days_remaining <= 0:
                        icon = "⚠️" if days_remaining > 0 else "🚨"
                        notification_manager.send_notification(
                            f"{icon} SSL Expiry Warning: {host.name}",
                            f"Host: {host.name}\nDays Remaining: {days_remaining}\nURL: {host.ip_address}",
                        )
                else:
                    host.ssl_error = "Failed to retrieve certificate"
            except Exception as e:
                host.ssl_error = str(e)
                logger.error(f"Error checking SSL for {host.name}: {e}")
        db.commit()
    except Exception as e:
        logger.error(f"Error in check_ssl_job: {e}")
    finally:
        db.close()


def check_ssl_expiry(host: str, port: int = 443):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.strptime(cert["notAfter"], r"%b %d %H:%M:%S %Y %Z")
                return (expiry_date - datetime.utcnow()).days
    except Exception as e:
        logger.warning(f"SSL check failed for {host}: {e}")
        return None


def _is_in_maintenance_window(host: HostDB) -> bool:
    """Returns True if host is currently in a scheduled maintenance window."""
    if host.maintenance:
        return True
    if host.maintenance_start and host.maintenance_end:
        now = datetime.utcnow()
        return host.maintenance_start <= now <= host.maintenance_end
    return False


def ping_host(host_id: int, ip_address: str, name: str, port: int = None, monitor_type: str = "icmp", expected_status: int = 200):
    try:
        latency_val = -1.0

        if monitor_type == "heartbeat":
            # Heartbeat monitors don't get polled — they receive pushes via /heartbeat/{slug}
            # We just check if a heartbeat was received recently
            db = SessionLocal()
            try:
                host = db.query(HostDB).filter(HostDB.id == host_id).first()
                if host and host.heartbeat_interval:
                    cutoff = datetime.utcnow() - timedelta(seconds=host.heartbeat_interval * 2)
                    last = db.query(PingResultDB).filter(
                        PingResultDB.host_id == host_id,
                        PingResultDB.timestamp >= cutoff
                    ).order_by(PingResultDB.timestamp.desc()).first()
                    latency_val = last.latency if last and last.latency is not None else -1.0
            finally:
                db.close()
        elif monitor_type == "http":
            is_up, latency_val, _ = check_http(ip_address, expected_status)
            if not is_up:
                latency_val = -1.0
        elif monitor_type == "tcp" and port:
            try:
                start_time = time.time()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((ip_address, port))
                end_time = time.time()
                sock.close()
                if result == 0:
                    latency_val = (end_time - start_time) * 1000
                    logger.info(f"TCP {name} ({ip_address}:{port}): {latency_val:.2f}ms")
                else:
                    logger.warning(f"TCP failed for {name} ({ip_address}:{port})")
            except Exception as e:
                logger.error(f"TCP error for {name}: {e}")
        else:
            latency = ping(ip_address, unit="ms", timeout=2)
            if latency is None:
                logger.warning(f"Ping timeout for {name} ({ip_address})")
            else:
                latency_val = float(latency)
                logger.info(f"Ping {name} ({ip_address}): {latency_val:.2f}ms")

        # Save result
        db = SessionLocal()
        try:
            db.add(PingResultDB(
                host_id=host_id,
                latency=latency_val if latency_val >= 0 else None,
            ))
            db.commit()
        except Exception as e:
            logger.error(f"Error saving ping result: {e}")
            db.rollback()
        finally:
            db.close()

        # Status change detection + alerts
        db = SessionLocal()
        try:
            host = db.query(HostDB).filter(HostDB.id == host_id).first()
            if not host:
                return

            current_status = "UP" if latency_val >= 0 else "DOWN"

            if host.last_status != current_status:
                logger.info(f"{name} status: {host.last_status} → {current_status}")
                if not _is_in_maintenance_window(host):
                    icon = "🔴" if current_status == "DOWN" else "🟢"
                    notification_manager.send_notification(
                        f"{icon} Host {name} is {current_status}",
                        f"Host: {name} ({ip_address})\nState: {current_status}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    )
                host.last_status = current_status
                db.commit()

            # Latency threshold alert
            if (
                current_status == "UP"
                and host.latency_threshold_ms
                and latency_val > host.latency_threshold_ms
                and not _is_in_maintenance_window(host)
            ):
                notification_manager.send_notification(
                    f"⚡ High Latency: {name}",
                    f"Host: {name} ({ip_address})\nLatency: {latency_val:.2f}ms\nThreshold: {host.latency_threshold_ms:.0f}ms",
                )
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error checking {name}: {e}")


def check_heartbeat_timeouts():
    """Check heartbeat-type hosts for missed heartbeats."""
    db = SessionLocal()
    try:
        hosts = db.query(HostDB).filter(
            HostDB.monitor_type == "heartbeat",
            HostDB.enabled == True,
            HostDB.heartbeat_interval != None,
        ).all()

        if not hosts:
            return

        host_ids = [host.id for host in hosts]

        # Optimize: single query to get the latest ping timestamp for all heartbeat hosts
        latest_pings = (
            db.query(PingResultDB.host_id, func.max(PingResultDB.timestamp).label("max_ts"))
            .filter(PingResultDB.host_id.in_(host_ids))
            .group_by(PingResultDB.host_id)
            .all()
        )

        latest_ping_map = {row.host_id: row.max_ts for row in latest_pings}

        for host in hosts:
            cutoff = datetime.utcnow() - timedelta(seconds=host.heartbeat_interval * 2)
            last_timestamp = latest_ping_map.get(host.id)

            last = True if last_timestamp and last_timestamp >= cutoff else False
            new_status = "UP" if last else "DOWN"

            if host.last_status != new_status:
                host.last_status = new_status
                db.commit()
                if new_status == "DOWN" and not _is_in_maintenance_window(host):
                    notification_manager.send_notification(
                        f"🔴 Host {host.name} is DOWN",
                        f"Host: {host.name}\nHeartbeat missed (expected every {host.heartbeat_interval}s).",
                    )
    except Exception as e:
        logger.error(f"Error in check_heartbeat_timeouts: {e}")
    finally:
        db.close()


def update_jobs():
    db: Session = SessionLocal()
    try:
        hosts = db.query(HostDB).filter(HostDB.enabled == True).all()
        enabled_host_ids = {h.id: h for h in hosts}
        current_jobs = scheduler.get_jobs()
        ping_jobs = {job.id: job for job in current_jobs if job.id.startswith("ping_")}
        processed_host_ids = set()

        for job_id, job in ping_jobs.items():
            try:
                host_id = int(job_id.replace("ping_", ""))
                if host_id not in enabled_host_ids:
                    scheduler.remove_job(job_id)
                else:
                    host = enabled_host_ids[host_id]
                    processed_host_ids.add(host_id)
                    current_interval = job.trigger.interval.total_seconds()
                    if current_interval != host.interval:
                        scheduler.reschedule_job(job_id, trigger="interval", seconds=host.interval)
            except ValueError:
                continue

        for host_id, host in enabled_host_ids.items():
            if host_id not in processed_host_ids:
                scheduler.add_job(
                    ping_host,
                    "interval",
                    seconds=host.interval,
                    args=[host.id, host.ip_address, host.name, host.port, host.monitor_type, host.expected_status_code],
                    id=f"ping_{host.id}",
                    replace_existing=True,
                )
        logger.info(f"Scheduler synced. Active ping jobs: {len(enabled_host_ids)}")
    except Exception as e:
        logger.error(f"Error updating jobs: {e}")
    finally:
        db.close()

    if not scheduler.get_job("check_public_ip"):
        scheduler.add_job(check_public_ip, "interval", minutes=30, id="check_public_ip", replace_existing=True)
        scheduler.add_job(check_public_ip)

    if not scheduler.get_job("run_speedtest"):
        scheduler.add_job(run_speedtest, "interval", hours=6, id="run_speedtest", replace_existing=True)

    scheduler.add_job(calculate_average_latency, "interval", hours=6, id="calculate_average_latency", replace_existing=True)
    scheduler.add_job(calculate_average_latency)

    scheduler.add_job(cleanup_old_data, "interval", days=1, id="cleanup_old_data", replace_existing=True)

    scheduler.add_job(check_ssl_job, "interval", days=1, id="check_ssl_job", replace_existing=True)
    scheduler.add_job(check_ssl_job)

    if not scheduler.get_job("check_heartbeat_timeouts"):
        scheduler.add_job(check_heartbeat_timeouts, "interval", minutes=2, id="check_heartbeat_timeouts", replace_existing=True)


def start_scheduler():
    update_jobs()
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def calculate_average_latency():
    db: Session = SessionLocal()
    try:
        hosts = db.query(HostDB).filter(HostDB.enabled == True).all()
        cutoff_time = datetime.utcnow() - timedelta(hours=6)

        latency_results = (
            db.query(PingResultDB.host_id, func.avg(PingResultDB.latency).label("avg_latency"))
            .filter(
                PingResultDB.timestamp >= cutoff_time,
                PingResultDB.latency != None,
            )
            .group_by(PingResultDB.host_id)
            .all()
        )

        latency_map = {result.host_id: result.avg_latency for result in latency_results}

        for host in hosts:
            try:
                avg_latency = latency_map.get(host.id)
                if avg_latency is not None:
                    host.average_latency = avg_latency
            except Exception as e:
                logger.error(f"Error calculating latency for {host.name}: {e}")
        db.commit()
    except Exception as e:
        logger.error(f"Error in calculate_average_latency: {e}")
    finally:
        db.close()


def cleanup_old_data():
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        deleted_pings = db.query(PingResultDB).filter(PingResultDB.timestamp < cutoff_date).delete()
        deleted_speedtests = db.query(SpeedTestResultDB).filter(SpeedTestResultDB.timestamp < cutoff_date).delete()
        deleted_ips = db.query(PublicIPHistoryDB).filter(PublicIPHistoryDB.timestamp < cutoff_date).delete()
        db.commit()
        logger.info(f"Cleanup: {deleted_pings} pings, {deleted_speedtests} speedtests, {deleted_ips} IPs deleted.")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()
