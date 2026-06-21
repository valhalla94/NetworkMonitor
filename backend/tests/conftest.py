import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Must set env vars before importing app modules
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only-do-not-use")
os.environ.setdefault("ADMIN_PASSWORD", "testpassword123")


@pytest.fixture(scope="session")
def client():
    import database
    import models

    # Use in-memory SQLite for tests
    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    database.engine = test_engine
    database.SessionLocal = TestSession
    models.Base.metadata.create_all(bind=test_engine)

    from main import app

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    from database import get_db
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def auth_token(client):
    response = client.post("/token", data={"username": "admin", "password": "testpassword123"})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
