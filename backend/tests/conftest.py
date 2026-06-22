import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Force env vars before importing app modules — override any CI-set values so tests are self-contained
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-do-not-use"
os.environ["ADMIN_PASSWORD"] = "testpassword123"


@pytest.fixture(scope="function")
def db_session(client):
    """Provides a db session for direct DB manipulation in tests.
    Depends on `client` to ensure the test engine and SessionLocal are initialized.
    Since we use the test client's engine (in-memory SQLite), we yield a session.
    """
    import database
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(scope="session")
def db_session():
    import database
    import models

    # Use in-memory SQLite for tests. StaticPool keeps a single shared connection so
    # all sessions (and the TestClient's worker thread) see the same in-memory DB —
    # otherwise each new connection gets its own empty :memory: database.
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    database.engine = test_engine
    database.SessionLocal = TestSession
    models.Base.metadata.create_all(bind=test_engine)

    # Provide a session specifically for tests to interact with the database
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client(db_session):
    import database
    from main import app
    from database import get_db

    # Note: `database.SessionLocal` and `database.engine` are already set correctly
    # by the `db_session` fixture.
    def override_get_db():
        db = database.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def auth_token(client):
    response = client.post("/token", data={"username": "admin", "password": "testpassword123"})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
