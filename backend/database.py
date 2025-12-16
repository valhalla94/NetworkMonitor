import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# SQLite Setup
SQLITE_URL = "sqlite:///./data/hosts.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

# Enable WAL mode for better concurrency
from sqlalchemy import event
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# InfluxDB Setup - REMOVED
# Migrated to SQLite-only storage


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

    try:
        # Check if last_status column exists
        try:
            db.execute(text("SELECT last_status FROM hosts LIMIT 1"))
        except OperationalError:
            logger.info("Column 'last_status' missing in 'hosts' table. Adding it...")
            try:
                db.execute(text("ALTER TABLE hosts ADD COLUMN last_status VARCHAR DEFAULT 'UNKNOWN'"))
                db.commit()
                logger.info("Column 'last_status' added successfully.")
            except Exception as e:
                logger.error(f"Failed to add column 'last_status': {e}")
                db.rollback()
    except Exception as e:
        logger.error(f"Migration check failed for last_status: {e}")

    try:
        # Check if ssl_expiry_days column exists
        try:
            db.execute(text("SELECT ssl_expiry_days FROM hosts LIMIT 1"))
        except OperationalError:
            logger.info("Column 'ssl_expiry_days' missing in 'hosts' table. Adding it...")
            try:
                db.execute(text("ALTER TABLE hosts ADD COLUMN ssl_expiry_days INTEGER"))
                db.commit()
                logger.info("Column 'ssl_expiry_days' added successfully.")
            except Exception as e:
                logger.error(f"Failed to add column 'ssl_expiry_days': {e}")
                db.rollback()


        # Check if ssl_error column exists
        try:
            db.execute(text("SELECT ssl_error FROM hosts LIMIT 1"))
        except OperationalError:
            logger.info("Column 'ssl_error' missing in 'hosts' table. Adding it...")
            try:
                db.execute(text("ALTER TABLE hosts ADD COLUMN ssl_error VARCHAR"))
                db.commit()
                logger.info("Column 'ssl_error' added successfully.")
            except Exception as e:
                logger.error(f"Failed to add column 'ssl_error': {e}")
                db.rollback()

    except Exception as e:
        logger.error(f"Migration check failed for SSL columns: {e}")

    try:
         # Check if server_id column exists in speedtest_results
        try:
            db.execute(text("SELECT server_id FROM speedtest_results LIMIT 1"))
        except OperationalError:
            logger.info("Column 'server_id' missing in 'speedtest_results' table. Adding it...")
            try:
                db.execute(text("ALTER TABLE speedtest_results ADD COLUMN server_id INTEGER"))
                db.execute(text("ALTER TABLE speedtest_results ADD COLUMN server_name VARCHAR"))
                db.execute(text("ALTER TABLE speedtest_results ADD COLUMN server_country VARCHAR"))
                db.commit()
                logger.info("Speedtest columns added successfully.")
            except Exception as e:
                logger.error(f"Failed to add speedtest columns: {e}")
                db.rollback()
    except Exception as e:
        logger.error(f"Migration check failed for Speedtest columns: {e}")

    finally:
        db.close()
