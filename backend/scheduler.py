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
            
            # Check the last known IP from InfluxDB
            from database import query_api
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
                    args=[host.id, host.ip_address, host.name],
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
