import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# SQLite Setup
SQLITE_URL = "sqlite:///./data/hosts.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# InfluxDB Setup
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "my-super-secret-auth-token")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "my-org")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "network_monitor")

influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)
query_api = influx_client.query_api()

def migrate_db():
    """
    Checks for missing columns and adds them if necessary.
    This is a simple migration mechanism for SQLite.
    """
    from sqlalchemy import text
    from sqlalchemy.exc import OperationalError
    import logging
    
    logger = logging.getLogger(__name__)
    db = SessionLocal()
    try:
        # Check if hosts table exists first
        try:
            db.execute(text("SELECT 1 FROM hosts LIMIT 1"))
        except OperationalError:
             # Table doesn't exist yet, create_all will handle it
             return

        # Check if average_latency column exists
        try:
            db.execute(text("SELECT average_latency FROM hosts LIMIT 1"))
        except OperationalError:
            logger.info("Column 'average_latency' missing in 'hosts' table. Adding it...")
            try:
                db.execute(text("ALTER TABLE hosts ADD COLUMN average_latency FLOAT"))
                db.commit()
                logger.info("Column 'average_latency' added successfully.")
            except Exception as e:
                logger.error(f"Failed to add column 'average_latency': {e}")
                db.rollback()

        # Check if port column exists
        try:
            db.execute(text("SELECT port FROM hosts LIMIT 1"))
        except OperationalError:
            logger.info("Column 'port' missing in 'hosts' table. Adding it...")
            try:
                db.execute(text("ALTER TABLE hosts ADD COLUMN port INTEGER"))
                db.commit()
                logger.info("Column 'port' added successfully.")
            except Exception as e:
                logger.error(f"Failed to add column 'port': {e}")
                db.rollback()

        # Check if monitor_type column exists
        try:
            db.execute(text("SELECT monitor_type FROM hosts LIMIT 1"))
        except OperationalError:
            logger.info("Column 'monitor_type' missing in 'hosts' table. Adding it...")
            try:
                db.execute(text("ALTER TABLE hosts ADD COLUMN monitor_type VARCHAR DEFAULT 'icmp'"))
                db.commit()
                logger.info("Column 'monitor_type' added successfully.")
            except Exception as e:
                logger.error(f"Failed to add column 'monitor_type': {e}")
                db.rollback()

        # Check if ssl_monitor column exists
        try:
            db.execute(text("SELECT ssl_monitor FROM hosts LIMIT 1"))
        except OperationalError:
            logger.info("Column 'ssl_monitor' missing in 'hosts' table. Adding it...")
            try:
                db.execute(text("ALTER TABLE hosts ADD COLUMN ssl_monitor BOOLEAN DEFAULT 0"))
                db.commit()
                logger.info("Column 'ssl_monitor' added successfully.")
            except Exception as e:
                logger.error(f"Failed to add column 'ssl_monitor': {e}")
                db.rollback()

        # Check if expected_status_code column exists
        try:
            db.execute(text("SELECT expected_status_code FROM hosts LIMIT 1"))
        except OperationalError:
            logger.info("Column 'expected_status_code' missing in 'hosts' table. Adding it...")
            try:
                db.execute(text("ALTER TABLE hosts ADD COLUMN expected_status_code INTEGER DEFAULT 200"))
                db.commit()
                logger.info("Column 'expected_status_code' added successfully.")
            except Exception as e:
                logger.error(f"Failed to add column 'expected_status_code': {e}")
                db.rollback()

        # Check if group_name column exists
        try:
            db.execute(text("SELECT group_name FROM hosts LIMIT 1"))
        except OperationalError:
            logger.info("Column 'group_name' missing in 'hosts' table. Adding it...")
            try:
                db.execute(text("ALTER TABLE hosts ADD COLUMN group_name VARCHAR DEFAULT 'General'"))
                db.commit()
                logger.info("Column 'group_name' added successfully.")
            except Exception as e:
                logger.error(f"Failed to add column 'group_name': {e}")
                db.rollback()

        # Check if maintenance column exists
        try:
            db.execute(text("SELECT maintenance FROM hosts LIMIT 1"))
        except OperationalError:
            logger.info("Column 'maintenance' missing in 'hosts' table. Adding it...")
            try:
                db.execute(text("ALTER TABLE hosts ADD COLUMN maintenance BOOLEAN DEFAULT 0"))
                db.commit()
                logger.info("Column 'maintenance' added successfully.")
            except Exception as e:
                logger.error(f"Failed to add column 'maintenance': {e}")
                db.rollback()
    except Exception as e:
        logger.error(f"Migration check failed: {e}")
    finally:
        db.close()
