import time
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from database import SessionLocal, write_api, INFLUXDB_BUCKET, INFLUXDB_ORG
from models import HostDB
from ping3 import ping
from influxdb_client import Point
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def check_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        if response.status_code == 200:
            ip_address = response.json().get('ip')
            logger.info(f"Public IP: {ip_address}")
            
            point = (
                Point("public_ip_history")
                .field("ip_address", ip_address)
            )
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        else:
            logger.error(f"Failed to get public IP: {response.status_code}")
    except Exception as e:
        logger.error(f"Error checking public IP: {e}")

def ping_host(host_id: int, ip_address: str, name: str):
    try:
        latency = ping(ip_address, unit='ms', timeout=2)
        if latency is None:
            logger.warning(f"Ping timeout for {name} ({ip_address})")
            latency_val = -1.0 # Use -1 to indicate timeout/down in Influx
        else:
            latency_val = float(latency)
            logger.info(f"Ping {name} ({ip_address}): {latency_val}ms")

        point = (
            Point("ping_result")
            .tag("host_id", str(host_id))
            .tag("host_name", name)
            .tag("ip_address", ip_address)
            .field("latency", latency_val)
        )
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

    except Exception as e:
        logger.error(f"Error pinging {name}: {e}")

def update_jobs():
    """
    Syncs the scheduler jobs with the database.
    This is a naive implementation that removes all jobs and re-adds them.
    For production, a diff-based approach would be better, but this is sufficient for now.
    """
    scheduler.remove_all_jobs()
    db: Session = SessionLocal()
    try:
        hosts = db.query(HostDB).filter(HostDB.enabled == True).all()
        for host in hosts:
            scheduler.add_job(
                ping_host,
                'interval',
                seconds=host.interval,
                args=[host.id, host.ip_address, host.name],
                id=f"ping_{host.id}",
                replace_existing=True
            )
        logger.info(f"Updated scheduler with {len(hosts)} jobs.")
    finally:
        db.close()

    # Add public IP check job
    scheduler.add_job(
        check_public_ip,
        'interval',
        minutes=30,
        id='check_public_ip',
        replace_existing=True
    )
    logger.info("Added public IP check job.")

def start_scheduler():
    scheduler.start()
    update_jobs()
