from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health():
    """Health returns 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_cors_allows_the_frontend_dev_origin():
    """A preflight from the Vite dev server is allowed."""
    response = client.options(
        "/api/v1/users/me",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_rejects_unknown_origins():
    """Origins that are not configured get no CORS header."""
    response = client.get("/health", headers={"Origin": "http://evil.example"})
    assert "access-control-allow-origin" not in response.headers