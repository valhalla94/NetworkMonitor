def test_get_hosts_public(client):
    """GET /hosts/ is public (no auth needed for dashboard read access)."""
    response = client.get("/hosts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_host(client, auth_headers):
    response = client.post("/hosts/", json={
        "name": "Test Host",
        "ip_address": "10.0.0.1",
        "interval": 30,
        "monitor_type": "icmp",
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Host"
    assert data["ip_address"] == "10.0.0.1"
    return data["id"]


def test_get_host(client, auth_headers):
    # Create first
    create_resp = client.post("/hosts/", json={
        "name": "Host for Get Test",
        "ip_address": "10.0.0.2",
        "interval": 60,
    }, headers=auth_headers)
    host_id = create_resp.json()["id"]

    response = client.get(f"/hosts/{host_id}")
    assert response.status_code == 200
    assert response.json()["id"] == host_id


def test_delete_host(client, auth_headers):
    create_resp = client.post("/hosts/", json={
        "name": "Host to Delete",
        "ip_address": "10.0.0.3",
        "interval": 30,
    }, headers=auth_headers)
    host_id = create_resp.json()["id"]

    del_resp = client.delete(f"/hosts/{host_id}", headers=auth_headers)
    assert del_resp.status_code == 200

    get_resp = client.get(f"/hosts/{host_id}")
    assert get_resp.status_code == 404


def test_quick_ping_invalid_target(client):
    """Targets with shell metacharacters should be rejected."""
    response = client.post("/tools/ping", json={"target": "; rm -rf /"})
    assert response.status_code == 422


def test_quick_ping_valid_target_format(client):
    """Valid hostname format should pass validation (may fail ping itself)."""
    response = client.post("/tools/ping", json={"target": "127.0.0.1"})
    # 200 even if host unreachable — reachable field distinguishes
    assert response.status_code == 200


def test_network_status(client):
    response = client.get("/status")
    assert response.status_code == 200
    assert "status" in response.json()


def test_public_ip_history(client):
    response = client.get("/public-ip-history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_metrics_no_data(client, auth_headers):
    # Create host
    create_resp = client.post("/hosts/", json={
        "name": "Host Metrics No Data",
        "ip_address": "10.0.0.4",
        "interval": 30,
    }, headers=auth_headers)
    host_id = create_resp.json()["id"]

    # Request metrics
    response = client.get(f"/metrics/{host_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["uptime"] == 0
    assert data["avg_latency"] == 0
    assert data["data"] == []


def test_get_metrics_with_data(client, auth_headers, db_session):
    from datetime import datetime, timedelta
    import models

    # Create host
    create_resp = client.post("/hosts/", json={
        "name": "Host Metrics With Data",
        "ip_address": "10.0.0.5",
        "interval": 30,
    }, headers=auth_headers)
    host_id = create_resp.json()["id"]

    now = datetime.utcnow()
    # Insert some PingResultDB records
    pings = [
        models.PingResultDB(host_id=host_id, latency=10.0, timestamp=now - timedelta(minutes=10)),
        models.PingResultDB(host_id=host_id, latency=20.0, timestamp=now - timedelta(minutes=5)),
        models.PingResultDB(host_id=host_id, latency=None, timestamp=now - timedelta(minutes=2)), # Failed ping
    ]
    db_session.add_all(pings)
    db_session.commit()

    # Request metrics
    response = client.get(f"/metrics/{host_id}")
    assert response.status_code == 200
    data = response.json()

    # Uptime should be 2/3 = 66.666...%
    assert abs(data["uptime"] - 66.66) < 0.1
    # Avg latency should be (10.0 + 20.0) / 2 = 15.0
    assert data["avg_latency"] == 15.0
    # There should be 3 data points
    assert len(data["data"]) == 3


def test_get_metrics_range_filtering(client, auth_headers, db_session):
    from datetime import datetime, timedelta
    import models

    # Create host
    create_resp = client.post("/hosts/", json={
        "name": "Host Metrics Range Filter",
        "ip_address": "10.0.0.6",
        "interval": 30,
    }, headers=auth_headers)
    host_id = create_resp.json()["id"]

    now = datetime.utcnow()
    # Insert some PingResultDB records: one older than 1h, one newer
    pings = [
        models.PingResultDB(host_id=host_id, latency=50.0, timestamp=now - timedelta(hours=2)),
        models.PingResultDB(host_id=host_id, latency=10.0, timestamp=now - timedelta(minutes=30)),
    ]
    db_session.add_all(pings)
    db_session.commit()

    # Request metrics with range=-1h
    response = client.get(f"/metrics/{host_id}?range=-1h")
    assert response.status_code == 200
    data = response.json()

    # Should only return the ping from 30 mins ago
    assert len(data["data"]) == 1
    assert data["data"][0]["latency"] == 10.0
