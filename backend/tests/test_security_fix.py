import pytest

def test_uptime_history_unauthenticated(client):
    # This should return 401 once fixed.
    # Currently it returns 200 (or 404 if no data, but definitely not 401).
    response = client.get("/uptime/1")
    assert response.status_code == 401

def test_uptime_history_authenticated(client, auth_headers):
    # This should return 200 (or 404 if host not found, but not 401).
    # Since it's a mock DB, we expect it to return 200 with an empty list if host ID exists or 200 even if no data.
    # In main.py, get_uptime_history returns a list.
    response = client.get("/uptime/1", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
