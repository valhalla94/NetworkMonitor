
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

def test_network_status_requires_auth(client):
    """Test that /status requires authentication."""
    response = client.get("/status")
    assert response.status_code == 401

def test_network_status_no_data(client, auth_headers):
    db_session = get_test_db()
    response = client.get("/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UNKNOWN"
    assert data["details"] == "No data"
    assert data["global_avg_latency"] == 0

def test_network_status_up(client, auth_headers):
    db_session = get_test_db()
    host1 = HostDB(name="Host 1", ip_address="1.1.1.1", enabled=True, last_status="UP", average_latency=10.0)
    host2 = HostDB(name="Host 2", ip_address="2.2.2.2", enabled=True, last_status="UP", average_latency=20.0)
    db_session.add_all([host1, host2])
    db_session.commit()

    response = client.get("/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["reachable"] == 2
    assert data["total"] == 2
    assert data["global_avg_latency"] == 15.0

def test_network_status_down(client, auth_headers):
    db_session = get_test_db()
    host1 = HostDB(name="Host 1", ip_address="1.1.1.1", enabled=True, last_status="DOWN", average_latency=10.0)
    host2 = HostDB(name="Host 2", ip_address="2.2.2.2", enabled=True, last_status="UNKNOWN", average_latency=None)
    db_session.add_all([host1, host2])
    db_session.commit()

    response = client.get("/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DOWN"
    assert data["reachable"] == 0
    assert data["total"] == 2
    assert data["global_avg_latency"] == 0

def test_network_status_down_minority_reachable(client, auth_headers):
    db_session = get_test_db()
    # Create 3 hosts, only 1 is reachable -> 1/3 is not > 0.5 -> DOWN
    hosts = [HostDB(name=f"Host {i}", ip_address=f"1.1.1.{i}", enabled=True, last_status="DOWN") for i in range(1, 4)]
    hosts[0].last_status = "UP"
    hosts[0].average_latency = 50.0
    db_session.add_all(hosts)
    db_session.commit()

    response = client.get("/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DOWN"
    assert data["reachable"] == 1
    assert data["total"] == 3
    assert data["global_avg_latency"] == 50.0

def test_network_status_ignores_disabled(client, auth_headers):
    db_session = get_test_db()
    host1 = HostDB(name="Host 1", ip_address="1.1.1.1", enabled=False, last_status="UP", average_latency=10.0) # Disabled!
    host2 = HostDB(name="Host 2", ip_address="2.2.2.2", enabled=True, last_status="UP", average_latency=20.0) # Enabled!
    db_session.add_all([host1, host2])
    db_session.commit()

    response = client.get("/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["reachable"] == 1
    assert data["total"] == 1 # Total should be 1 because host1 is disabled
    assert data["global_avg_latency"] == 20.0

def test_network_status_ignores_old_pings(client, auth_headers):
    db_session = get_test_db()
    # this test relies on old behavior of ping cutoff, but the current behavior uses last_status directly
    # and last_status is maintained by the scheduler based on the most recent pings
    # we simulate the scheduler having set last_status to DOWN because of an old ping
    host1 = HostDB(name="Host 1", ip_address="1.1.1.1", enabled=True, last_status="DOWN")
    db_session.add(host1)
    db_session.commit()

    response = client.get("/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    # No recent pings mean reachable=0
    assert data["status"] == "DOWN"
    assert data["reachable"] == 0
    assert data["total"] == 1

def test_network_status_takes_latest_ping(client, auth_headers):
    db_session = get_test_db()
    # this test relies on old behavior of taking the latest ping, but the current behavior uses last_status directly
    host1 = HostDB(name="Host 1", ip_address="1.1.1.1", enabled=True, last_status="UP", average_latency=20.0)
    db_session.add(host1)
    db_session.commit()

    response = client.get("/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["reachable"] == 1
    assert data["total"] == 1
    assert data["global_avg_latency"] == 20.0
