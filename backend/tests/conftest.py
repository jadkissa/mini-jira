import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app

TEST_DATABASE_URL = "postgresql+psycopg://mini_jira:mini_jira@localhost:5432/mini_jira_test"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def client():
    """Give each test a clean database and an HTTP client pointed at the app."""
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        """Use the test database instead of the app's normal session."""
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        test_client.post(
            "/api/v1/users",
            json={
                "email": "tester@example.com",
                "password": "secret",
                "full_name": "Tester",
            },
        )
        login = test_client.post(
            "/api/v1/auth/login",
            json={"email": "tester@example.com", "password": "secret"},
        )
        token = login.json()["access_token"]
        test_client.headers["Authorization"] = f"Bearer {token}"
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
