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
