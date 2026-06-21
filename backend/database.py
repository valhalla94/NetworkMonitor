import os
import logging
import re
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

SQLITE_URL = "sqlite:///./data/hosts.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

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


# Column definitions: table → [(column_name, sql_type)]
_MIGRATIONS = {
    "hosts": [
        ("average_latency", "FLOAT"),
        ("port", "INTEGER"),
        ("monitor_type", "VARCHAR DEFAULT 'icmp'"),
        ("ssl_monitor", "BOOLEAN DEFAULT 0"),
        ("expected_status_code", "INTEGER DEFAULT 200"),
        ("group_name", "VARCHAR DEFAULT 'General'"),
        ("maintenance", "BOOLEAN DEFAULT 0"),
        ("last_status", "VARCHAR DEFAULT 'UNKNOWN'"),
        ("ssl_expiry_days", "INTEGER"),
        ("ssl_error", "VARCHAR"),
        ("latency_threshold_ms", "FLOAT"),
        ("heartbeat_slug", "VARCHAR"),
        ("heartbeat_interval", "INTEGER"),
        ("maintenance_start", "DATETIME"),
        ("maintenance_end", "DATETIME"),
    ],
    "speedtest_results": [
        ("server_id", "INTEGER"),
        ("server_name", "VARCHAR"),
        ("server_country", "VARCHAR"),
    ],
}


def is_valid_identifier(name: str) -> bool:
    """Validates that a string is a valid SQL identifier (table or column name)."""
    return bool(re.match(r"^[a-zA-Z0-9_]+$", name))


def is_valid_typedef(typedef: str) -> bool:
    """Validates that a string is a valid SQL type definition."""
    # Allow alphanumeric characters, spaces, single quotes, parentheses, commas, dots, and dashes
    return bool(re.match(r"^[a-zA-Z0-9_ \'\.\(\)\-,]+$", typedef))


def _add_column_if_missing(db, table: str, col: str, typedef: str):
    if not is_valid_identifier(table) or not is_valid_identifier(col) or not is_valid_typedef(typedef):
        logger.error(f"Invalid identifier or typedef: table='{table}', col='{col}', typedef='{typedef}'")
        return

    try:
        db.execute(text(f"SELECT {col} FROM {table} LIMIT 1"))
    except OperationalError:
        logger.info(f"Adding column '{col}' to '{table}'...")
        try:
            db.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {typedef}"))
            db.commit()
        except Exception as e:
            logger.error(f"Failed to add column '{col}' to '{table}': {e}")
            db.rollback()


def migrate_db():
    db = SessionLocal()
    try:
        # Skip if hosts table doesn't exist yet — create_all handles it
        try:
            db.execute(text("SELECT 1 FROM hosts LIMIT 1"))
        except OperationalError:
            return

        for table, columns in _MIGRATIONS.items():
            if not is_valid_identifier(table):
                logger.error(f"Invalid table name in migrations: '{table}'")
                continue

            # Skip tables that don't exist yet
            try:
                db.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
            except OperationalError:
                continue
            for col, typedef in columns:
                _add_column_if_missing(db, table, col, typedef)

    except Exception as e:
        logger.error(f"Migration failed: {e}")
    finally:
        db.close()
