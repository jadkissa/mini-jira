from tests.helpers import create_project


def _register(client):
    client.post(
        "/api/v1/users",
        json={"email": "ada@example.com", "password": "secret12", "full_name": "Ada"},
    )


def test_login_returns_tokens(client):
    """A correct password returns an access token and a refresh token."""
    _register(client)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "ada@example.com", "password": "secret12"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]


def test_login_with_wrong_password(client):
    """A wrong password returns 401."""
    _register(client)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "ada@example.com", "password": "wrongpass"},
    )

    assert response.status_code == 401


def test_refresh_returns_access_token(client):
    """A refresh token can be exchanged for a new access token."""
    _register(client)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "ada@example.com", "password": "secret12"},
    )

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login.json()["refresh_token"]},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_refresh_rejects_access_token(client):
    """An access token cannot be used as a refresh token."""
    _register(client)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "ada@example.com", "password": "secret12"},
    )

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login.json()["access_token"]},
    )

    assert response.status_code == 401


def test_projects_require_access_token(client):
    """Listing projects without a token returns 401."""
    client.headers.pop("Authorization")

    response = client.get("/api/v1/projects")

    assert response.status_code == 401


def test_projects_reject_refresh_token(client):
    """A refresh token cannot access protected routes."""
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tester@example.com", "password": "secret12"},
    )
    client.headers["Authorization"] = f"Bearer {login.json()['refresh_token']}"

    response = client.get("/api/v1/projects")

    assert response.status_code == 401


def test_me_returns_current_user(client):
    """The access token identifies the current user."""
    response = client.get("/api/v1/users/me")

    assert response.status_code == 200
    assert response.json()["email"] == "tester@example.com"


def test_register_does_not_return_password(client):
    """Registration returns the user and leaves the password out of the response."""
    response = client.post(
        "/api/v1/users",
        json={"email": "new@example.com", "password": "secret12", "full_name": "New"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.com"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email(client):
    """Registering the same email twice returns 409."""
    _register(client)

    response = client.post(
        "/api/v1/users",
        json={"email": "ada@example.com", "password": "secret12", "full_name": "Ada"},
    )

    assert response.status_code == 409


def test_login_unknown_email(client):
    """An unknown email returns the same 401 as a wrong password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "secret12"},
    )

    assert response.status_code == 401


def test_me_requires_access_token(client):
    """The current-user route rejects a missing token."""
    client.headers.pop("Authorization")

    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_tasks_require_access_token(client):
    """Listing tasks without a token returns 401."""
    project_id = create_project(client, "Demo").json()["id"]
    client.headers.pop("Authorization")

    response = client.get(f"/api/v1/projects/{project_id}/tasks")

    assert response.status_code == 401
