def test_login_success(client):
    response = client.post(
        "/token", data={"username": "admin", "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    response = client.post(
        "/token", data={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_login_wrong_username(client):
    response = client.post(
        "/token", data={"username": "notadmin", "password": "testpassword123"}
    )
    assert response.status_code == 401


def test_protected_endpoint_without_token(client):
    response = client.post(
        "/hosts/", json={"name": "test", "ip_address": "1.2.3.4", "interval": 30}
    )
    assert response.status_code == 401


def test_protected_endpoint_with_token(client, auth_headers):
    response = client.get("/settings", headers=auth_headers)
    assert response.status_code == 200
