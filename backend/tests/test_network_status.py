import pytest
from datetime import datetime, timedelta
import database
from models import HostDB, PingResultDB


def get_test_db():
    db = database.SessionLocal()
    try:
        # Before each test, ensure we start with a clean slate for these tables
        db.query(PingResultDB).delete()
        db.query(HostDB).delete()
        db.commit()
        return db
    finally:
        pass


def test_network_status_no_data(client):
    db_session = get_test_db()
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UNKNOWN"
    assert data["details"] == "No data"
    assert data["global_avg_latency"] == 0


def test_network_status_up(client):
    db_session = get_test_db()
    host1 = HostDB(name="Host 1", ip_address="1.1.1.1", enabled=True)
    host2 = HostDB(name="Host 2", ip_address="2.2.2.2", enabled=True)
    db_session.add_all([host1, host2])
    db_session.commit()

    now = datetime.utcnow()
    ping1 = PingResultDB(
        host_id=host1.id, latency=10.0, timestamp=now - timedelta(minutes=1)
    )
    ping2 = PingResultDB(
        host_id=host2.id, latency=20.0, timestamp=now - timedelta(minutes=1)
    )
    db_session.add_all([ping1, ping2])
    db_session.commit()

    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["reachable"] == 2
    assert data["total"] == 2
    assert data["global_avg_latency"] == 15.0


def test_network_status_down(client):
    db_session = get_test_db()
    host1 = HostDB(name="Host 1", ip_address="1.1.1.1", enabled=True)
    host2 = HostDB(name="Host 2", ip_address="2.2.2.2", enabled=True)
    db_session.add_all([host1, host2])
    db_session.commit()

    now = datetime.utcnow()
    # One is unreachable (latency=None)
    ping1 = PingResultDB(
        host_id=host1.id, latency=None, timestamp=now - timedelta(minutes=1)
    )
    # One has no recent ping
    # So both are effectively down
    db_session.add(ping1)
    db_session.commit()

    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DOWN"
    assert data["reachable"] == 0
    assert data["total"] == 2
    assert data["global_avg_latency"] == 0


def test_network_status_down_minority_reachable(client):
    db_session = get_test_db()
    # Create 3 hosts, only 1 is reachable -> 1/3 is not > 0.5 -> DOWN
    hosts = [
        HostDB(name=f"Host {i}", ip_address=f"1.1.1.{i}", enabled=True)
        for i in range(1, 4)
    ]
    db_session.add_all(hosts)
    db_session.commit()

    now = datetime.utcnow()
    # Only host 1 gets a successful ping
    ping1 = PingResultDB(
        host_id=hosts[0].id, latency=50.0, timestamp=now - timedelta(minutes=1)
    )
    ping2 = PingResultDB(
        host_id=hosts[1].id, latency=None, timestamp=now - timedelta(minutes=1)
    )
    db_session.add_all([ping1, ping2])
    db_session.commit()

    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DOWN"
    assert data["reachable"] == 1
    assert data["total"] == 3
    assert data["global_avg_latency"] == 50.0


def test_network_status_ignores_disabled(client):
    db_session = get_test_db()
    host1 = HostDB(name="Host 1", ip_address="1.1.1.1", enabled=False)  # Disabled!
    host2 = HostDB(name="Host 2", ip_address="2.2.2.2", enabled=True)  # Enabled!
    db_session.add_all([host1, host2])
    db_session.commit()

    now = datetime.utcnow()
    ping1 = PingResultDB(
        host_id=host1.id, latency=10.0, timestamp=now - timedelta(minutes=1)
    )
    ping2 = PingResultDB(
        host_id=host2.id, latency=20.0, timestamp=now - timedelta(minutes=1)
    )
    db_session.add_all([ping1, ping2])
    db_session.commit()

    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["reachable"] == 1
    assert data["total"] == 1  # Total should be 1 because host1 is disabled
    assert data["global_avg_latency"] == 20.0


def test_network_status_ignores_old_pings(client):
    db_session = get_test_db()
    host1 = HostDB(name="Host 1", ip_address="1.1.1.1", enabled=True)
    db_session.add(host1)
    db_session.commit()

    now = datetime.utcnow()
    # Ping is 6 minutes old, cutoff is 5 minutes
    ping1 = PingResultDB(
        host_id=host1.id, latency=10.0, timestamp=now - timedelta(minutes=6)
    )
    db_session.add(ping1)
    db_session.commit()

    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    # No recent pings mean reachable=0
    assert data["status"] == "DOWN"
    assert data["reachable"] == 0
    assert data["total"] == 1


def test_network_status_takes_latest_ping(client):
    db_session = get_test_db()
    host1 = HostDB(name="Host 1", ip_address="1.1.1.1", enabled=True)
    db_session.add(host1)
    db_session.commit()

    now = datetime.utcnow()
    # Old ping
    ping1 = PingResultDB(
        host_id=host1.id, latency=10.0, timestamp=now - timedelta(minutes=4)
    )
    # Latest ping (this should be the one taken)
    ping2 = PingResultDB(
        host_id=host1.id, latency=20.0, timestamp=now - timedelta(minutes=1)
    )
    db_session.add_all([ping1, ping2])
    db_session.commit()

    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["reachable"] == 1
    assert data["total"] == 1
    assert data["global_avg_latency"] == 20.0
