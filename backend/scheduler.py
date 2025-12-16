import time
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from database import SessionLocal, write_api, query_api, INFLUXDB_BUCKET, INFLUXDB_ORG
from models import HostDB
from ping3 import ping
from influxdb_client import Point
import logging
import requests
import subprocess
import json
import ssl
from datetime import datetime
from urllib.parse import urlparse

from notifications import notification_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def check_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        if response.status_code == 200:
            ip_address = response.json().get('ip')
            logger.info(f"Public IP: {ip_address}")
            
            # Check the last known IP from InfluxDB
            query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
              |> range(start: -30d)
              |> filter(fn: (r) => r["_measurement"] == "public_ip_history")
              |> filter(fn: (r) => r["_field"] == "ip_address")
              |> last()
            '''
            result = query_api.query(org=INFLUXDB_ORG, query=query)
            
            last_ip = None
            for table in result:
                for record in table.records:
                    last_ip = record.get_value()
                    break
            
            # Only write to InfluxDB if the IP has changed
            if last_ip != ip_address:
                logger.info(f"Public IP changed from {last_ip} to {ip_address}")
                point = (
                    Point("public_ip_history")
                    .field("ip_address", ip_address)
                )
                write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
            else:
                logger.info(f"Public IP unchanged: {ip_address}")
        else:
            logger.error(f"Failed to get public IP: {response.status_code}")
    except Exception as e:
        logger.error(f"Error checking public IP: {e}")

def run_speedtest():
    logger.info("Starting Internet Speed Test...")
    try:
        # Run speedtest-cli
        # We use --secure to use HTTPS
        cmd = ["speedtest-cli", "--json", "--secure"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            logger.error(f"Speedtest failed: {result.stderr}")
            return

        data = json.loads(result.stdout)
        
        download_mbps = data["download"] / 1_000_000
        upload_mbps = data["upload"] / 1_000_000
        ping_ms = data["ping"]
        
        logger.info(f"Speedtest Result: D:{download_mbps:.2f} Mbps, U:{upload_mbps:.2f} Mbps, P:{ping_ms:.2f} ms")

        point = (
            Point("speedtest_result")
            .field("download", float(download_mbps))
            .field("upload", float(upload_mbps))
            .field("ping", float(ping_ms))
            .field("server_id", data["server"]["id"])
            .field("server_name", data["server"]["name"])
            .field("server_country", data["server"]["country"])
        )
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        
    except Exception as e:
        logger.error(f"Error running speedtest: {e}")

import socket

def check_http(url: str, expected_status: int = 200, timeout: int = 5):
    try:
        if not url.startswith('http'):
            url = f"http://{url}"
            
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        end_time = time.time()
        
        latency = (end_time - start_time) * 1000
        status_code = response.status_code
        is_up = status_code == expected_status
        
        return is_up, latency, status_code
    except Exception as e:
        logger.warning(f"HTTP Check failed for {url}: {e}")
        return False, -1.0, 0

def check_ssl_expiry(host: str, port: int = 443):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.strptime(cert['notAfter'], r'%b %d %H:%M:%S %Y %Z')
                days_remaining = (expiry_date - datetime.utcnow()).days
                return days_remaining
    except Exception as e:
        logger.warning(f"SSL Check failed for {host}: {e}")
        return None

def ping_host(host_id: int, ip_address: str, name: str, port: int = None, monitor_type: str = 'icmp', ssl_monitor: bool = False, expected_status: int = 200):
    try:
        latency_val = -1.0
        status_code = 0
        ssl_days = None
        
        # 1. Perform Connectivity Check based on Monitor Type
        if monitor_type == 'http':
            is_up, latency_val, status_code = check_http(ip_address, expected_status)
            if not is_up:
                latency_val = -1.0 # Mark as down
        elif monitor_type == 'tcp' and port:
            # TCP Check
            try:
                start_time = time.time()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((ip_address, port))
                end_time = time.time()
                sock.close()
                
                if result == 0:
                    latency_val = (end_time - start_time) * 1000
                    logger.info(f"TCP Check {name} ({ip_address}:{port}): {latency_val:.2f}ms")
                else:
                    logger.warning(f"TCP Check failed for {name} ({ip_address}:{port})")
            except Exception as e:
                logger.error(f"TCP Check error for {name}: {e}")
        else:
            # ICMP Ping (Default)
            latency = ping(ip_address, unit='ms', timeout=2)
            if latency is None:
                logger.warning(f"Ping timeout for {name} ({ip_address})")
            else:
                latency_val = float(latency)
                logger.info(f"Ping {name} ({ip_address}): {latency_val}ms")

        # 2. Perform SSL Check if enabled
        if ssl_monitor:
            # Extract hostname from URL if needed
            target_host = ip_address
            if target_host.startswith('http'):
                 parsed = urlparse(target_host)
                 target_host = parsed.netloc.split(':')[0] # Remove port if present
            
            ssl_days = check_ssl_expiry(target_host, port if port else 443)
            if ssl_days is not None:
                logger.info(f"SSL Check {name}: {ssl_days} days remaining")

        # 3. Write to InfluxDB
        point = (
            Point("ping_result")
            .tag("host_id", str(host_id))
            .tag("host_name", name)
            .tag("ip_address", ip_address)
            .tag("monitor_type", monitor_type)
            .field("latency", latency_val)
        )
        
        if port:
            point = point.tag("port", str(port))
            
        if status_code > 0:
             point = point.field("http_status", int(status_code))
             
        if ssl_days is not None:
            point = point.field("ssl_expiry_days", int(ssl_days))
            
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

        # 4. Check for Status Change and Alert
        db = SessionLocal()
        host = db.query(HostDB).filter(HostDB.id == host_id).first()
        
        current_status = "UP" if latency_val >= 0 else "DOWN"
        
        if host and host.last_status != current_status:
            logger.info(f"Host {name} status changed: {host.last_status} -> {current_status}")
            
            # Send Notification if not in maintenance
            if not host.maintenance:
                icon = "🔴" if current_status == "DOWN" else "🟢"
                title = f"{icon} Host {name} is {current_status}"
                body = f"Host: {name} ({ip_address})\nState: {current_status}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                # Add detail for DOWN
                if current_status == "DOWN":
                    body += "\nDid not respond to ping/check."
                
                notification_manager.send_notification(title, body)
            else:
                logger.info(f"Notification suppressed for {name} due to maintenance mode.")
            
            # Update last_status
            host.last_status = current_status
            db.commit()
            
        # Check for SSL Expiry Alert (e.g. < 7 days) if not already alerted roughly?
        # For simplicity, we won't state-track SSL alerts perfectly here to avoid spam, 
        # but a simple log for now. A real system needs a separate 'last_ssl_alert' timestamp.
        if ssl_days is not None and ssl_days < 7:
             logger.warning(f"SSL Certificate for {name} expires in {ssl_days} days!")
             
        db.close()

    except Exception as e:
        logger.error(f"Error checking {name}: {e}")

def update_jobs():
    """
    Syncs the scheduler jobs with the database using a diff-based approach.
    Only adds/removes/updates jobs that have changed.
    """
    db: Session = SessionLocal()
    try:
        # Get all enabled hosts from DB
        hosts = db.query(HostDB).filter(HostDB.enabled == True).all()
        enabled_host_ids = {h.id: h for h in hosts}
        
        # Get all current ping jobs
        current_jobs = scheduler.get_jobs()
        ping_jobs = {job.id: job for job in current_jobs if job.id.startswith('ping_')}
        
        # Track which hosts we've processed from the existing jobs
        processed_host_ids = set()
        
        # 1. Remove jobs for hosts that are no longer enabled or exist
        # 2. Update jobs if interval changed
        for job_id, job in ping_jobs.items():
            try:
                host_id = int(job_id.replace('ping_', ''))
                
                if host_id not in enabled_host_ids:
                    scheduler.remove_job(job_id)
                    logger.info(f"Removed job for host {host_id}")
                else:
                    host = enabled_host_ids[host_id]
                    processed_host_ids.add(host_id)
                    
                    # Check if interval changed
                    # job.trigger.interval is a timedelta
                    current_interval = job.trigger.interval.total_seconds()
                    if current_interval != host.interval:
                        scheduler.reschedule_job(job_id, trigger='interval', seconds=host.interval)
                        logger.info(f"Updated interval for host {host.name} to {host.interval}s")
            except ValueError:
                continue # Not a standard ping job ID
                
        # 3. Add new jobs for hosts that don't have one yet
        for host_id, host in enabled_host_ids.items():
            if host_id not in processed_host_ids:
                scheduler.add_job(
                    ping_host,
                    'interval',
                    seconds=host.interval,
                    args=[host.id, host.ip_address, host.name, host.port, host.monitor_type, host.ssl_monitor, host.expected_status_code],
                    id=f"ping_{host.id}",
                    replace_existing=True
                )
                logger.info(f"Added job for host {host.name}")
                
        logger.info(f"Scheduler synced. Active ping jobs: {len(enabled_host_ids)}")
        
    except Exception as e:
        logger.error(f"Error updating jobs: {e}")
    finally:
        db.close()

    # Ensure static jobs exist
    if not scheduler.get_job('check_public_ip'):
        scheduler.add_job(
            check_public_ip,
            'interval',
            minutes=30,
            id='check_public_ip',
            replace_existing=True
        )
        logger.info("Added public IP check job.")

    # Add speedtest job (every 6 hours)
    if not scheduler.get_job('run_speedtest'):
        scheduler.add_job(
            run_speedtest,
            'interval',
            hours=6,
            id='run_speedtest',
            replace_existing=True
        )
        logger.info("Added speedtest job.")


    # Add average latency calculation job
    scheduler.add_job(
        calculate_average_latency,
        'interval',
        hours=6,
        id='calculate_average_latency',
        replace_existing=True
    )
    logger.info("Added average latency calculation job.")
    
    # Run immediately
    scheduler.add_job(calculate_average_latency)

def start_scheduler():
    update_jobs()
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")

def calculate_average_latency():
    """
    Calculates the average latency for each host over the last 6 hours
    and updates the database.
    """
    logger.info("Starting average latency calculation...")
    db: Session = SessionLocal()
    try:
        hosts = db.query(HostDB).filter(HostDB.enabled == True).all()
        for host in hosts:
            try:
                # Query InfluxDB for mean latency over last 6 hours
                query = f'''
                from(bucket: "{INFLUXDB_BUCKET}")
                  |> range(start: -6h)
                  |> filter(fn: (r) => r["_measurement"] == "ping_result")
                  |> filter(fn: (r) => r["host_id"] == "{host.id}")
                  |> filter(fn: (r) => r["_field"] == "latency")
                  |> filter(fn: (r) => r["_value"] >= 0)
                  |> mean()
                '''
                result = query_api.query(org=INFLUXDB_ORG, query=query)
                
                avg_latency = None
                for table in result:
                    for record in table.records:
                        avg_latency = record.get_value()
                        break
                
                if avg_latency is not None:
                    host.average_latency = avg_latency
                    logger.info(f"Updated average latency for {host.name}: {avg_latency:.2f}ms")
                else:
                    logger.info(f"No latency data found for {host.name} in last 6h")
                    
            except Exception as e:
                logger.error(f"Error calculating latency for {host.name}: {e}")
        
        db.commit()
        logger.info("Average latency calculation completed.")
        
    except Exception as e:
        logger.error(f"Error in calculate_average_latency: {e}")
    finally:
        db.close()
