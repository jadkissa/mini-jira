from app.models.user import User
from tests.conftest import TestingSessionLocal
from tests.helpers import create_project, login_as, register


def _make_superuser(email: str) -> None:
    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.email == email).one()
        user.is_superuser = True
        db.commit()
    finally:
        db.close()


def test_user_can_update_and_delete_self(client):
    me = client.get("/api/v1/users/me").json()
    response = client.patch(f"/api/v1/users/{me['id']}", json={"full_name": "New Name"})
    assert response.status_code == 200
    assert response.json()["full_name"] == "New Name"
    assert client.delete(f"/api/v1/users/{me['id']}").status_code == 204


def test_user_cannot_update_or_delete_others(client):
    other = register(client, "other@example.com", "Other")
    response = client.patch(f"/api/v1/users/{other['id']}", json={"password": "hacked"})
    assert response.status_code == 403
    assert client.delete(f"/api/v1/users/{other['id']}").status_code == 403


def test_user_cannot_grant_themselves_superuser(client):
    me = client.get("/api/v1/users/me").json()
    response = client.patch(f"/api/v1/users/{me['id']}", json={"is_superuser": True})
    assert response.status_code == 403
    response = client.patch(f"/api/v1/users/{me['id']}", json={"is_active": False})
    assert response.status_code == 403


def test_email_change_to_taken_email_conflicts(client):
    register(client, "taken@example.com", "Taken")
    me = client.get("/api/v1/users/me").json()
    response = client.patch(f"/api/v1/users/{me['id']}", json={"email": "taken@example.com"})
    assert response.status_code == 409


def test_superuser_can_manage_other_users(client):
    other = register(client, "other@example.com", "Other")
    register(client, "boss@example.com", "Boss")
    _make_superuser("boss@example.com")
    login_as(client, "boss@example.com")
    response = client.patch(f"/api/v1/users/{other['id']}", json={"full_name": "Renamed"})
    assert response.status_code == 200
    assert client.patch(f"/api/v1/users/{other['id']}", json={"is_active": False}).status_code == 200
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "other@example.com", "password": "secret"},
    )
    assert login.status_code == 403
    assert client.delete(f"/api/v1/users/{other['id']}").status_code == 204


def test_superuser_has_full_access_to_teams(client):
    project_id = create_project(client).json()["id"]
    team_id = client.get(f"/api/v1/projects/{project_id}").json()["team_id"]
    task_id = client.post(f"/api/v1/projects/{project_id}/tasks", json={"title": "T"}).json()["id"]

    register(client, "boss@example.com", "Boss")
    _make_superuser("boss@example.com")
    login_as(client, "boss@example.com")

    assert [t["id"] for t in client.get("/api/v1/teams").json()] == [team_id]
    assert [p["id"] for p in client.get("/api/v1/projects").json()] == [project_id]
    assert client.get(f"/api/v1/tasks/{task_id}").status_code == 200
    assert client.patch(f"/api/v1/projects/{project_id}", json={"name": "Mine"}).status_code == 200
    assert client.delete(f"/api/v1/tasks/{task_id}").status_code == 204
    assert client.delete(f"/api/v1/teams/{team_id}").status_code == 204


def test_superuser_gets_404_for_missing_team(client):
    register(client, "boss@example.com", "Boss")
    _make_superuser("boss@example.com")
    login_as(client, "boss@example.com")
    assert client.get("/api/v1/teams/999").status_code == 404
