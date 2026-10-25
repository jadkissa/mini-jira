def create_project(client, name="Demo", description=None):
    """Create a team owned by the logged-in user, then a project on it."""
    team = client.post("/api/v1/teams", json={"name": f"{name} team"}).json()
    body = {"name": name}
    if description is not None:
        body["description"] = description
    return client.post(f"/api/v1/teams/{team['id']}/projects", json=body)


def register(client, email: str, full_name: str):
    """Register a user and return the response body."""
    return client.post(
        "/api/v1/users",
        json={"email": email, "password": "secret", "full_name": full_name},
    ).json()


def login_as(client, email: str) -> None:
    """Replace the client's access token with this user's token."""
    token = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "secret"},
    ).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
