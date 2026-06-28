import pytest
from sqlalchemy import text
from sqlalchemy.pool import StaticPool
import database


def test_migrate_db_skips_if_no_hosts_table(monkeypatch):
    """Test that migrate_db exits cleanly if the hosts table does not exist."""

    # Create an empty in-memory SQLite DB
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", TestSession)

    # There are no tables created yet
    database.migrate_db()

    # Verify no tables were created by the migration script
    db = TestSession()
    try:
        result = db.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        ).fetchall()
        assert len(result) == 0
    finally:
        db.close()


def test_migrate_db_adds_missing_columns(monkeypatch):
    """Test that migrate_db successfully adds missing columns to existing tables."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(database, "SessionLocal", TestSession)

    db = TestSession()
    try:
        # Create an older version of the schema manually
        # 'hosts' table with missing columns
        db.execute(text("""
            CREATE TABLE hosts (
                id INTEGER PRIMARY KEY,
                name VARCHAR,
                ip_address VARCHAR
            )
        """))

        # 'speedtest_results' table with missing columns
        db.execute(text("""
            CREATE TABLE speedtest_results (
                id INTEGER PRIMARY KEY,
                download FLOAT,
                upload FLOAT,
                ping FLOAT
            )
        """))
        db.commit()
    finally:
        db.close()

    # Run the migration
    database.migrate_db()

    # Verify that columns from _MIGRATIONS have been added
    db = TestSession()
    try:
        # Check hosts table
        result_hosts = db.execute(text("PRAGMA table_info(hosts)")).fetchall()
        column_names_hosts = [row[1] for row in result_hosts]

        # hosts table already had id, name, ip_address
        assert "average_latency" in column_names_hosts
        assert "port" in column_names_hosts
        assert "maintenance_end" in column_names_hosts

        # Check speedtest_results table
        result_speedtest = db.execute(
            text("PRAGMA table_info(speedtest_results)")
        ).fetchall()
        column_names_speedtest = [row[1] for row in result_speedtest]

        assert "server_id" in column_names_speedtest
        assert "server_country" in column_names_speedtest
    finally:
        db.close()
