from tests.helpers import create_project, login_as, register


def _team_with_task(client):
    project = create_project(client, "Demo")
    project_id = project.json()["id"]
    team_id = project.json()["team_id"]
    task_id = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "A"},
    ).json()["id"]
    return team_id, project_id, task_id


def test_owner_can_delete_team_and_invite_admin(client):
    """The owner may invite an admin and delete the team."""
    team_id, _, _ = _team_with_task(client)
    admin = register(client, "admin@example.com", "Admin")

    invited = client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": admin["id"], "role": "admin"},
    )
    assert invited.status_code == 201
    assert client.delete(f"/api/v1/teams/{team_id}").status_code == 204


def test_member_can_view_and_edit_tasks_only(client):
    """A member may view and edit tasks, and nothing that changes the team."""
    team_id, project_id, task_id = _team_with_task(client)
    member = register(client, "member@example.com", "Member")
    client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": member["id"], "role": "member"},
    )
    login_as(client, "member@example.com")

    assert client.get(f"/api/v1/teams/{team_id}").status_code == 200
    assert client.get(f"/api/v1/projects/{project_id}").status_code == 200
    assert client.get(f"/api/v1/tasks/{task_id}").status_code == 200
    assert client.patch(f"/api/v1/tasks/{task_id}", json={"title": "Edited"}).status_code == 200
    assert client.post(f"/api/v1/teams/{team_id}/projects", json={"name": "Nope"}).status_code == 403
    assert client.patch(f"/api/v1/projects/{project_id}", json={"name": "Nope"}).status_code == 403
    assert client.delete(f"/api/v1/projects/{project_id}").status_code == 403
    assert client.delete(f"/api/v1/tasks/{task_id}").status_code == 403
    assert client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": member["id"], "role": "member"},
    ).status_code == 403
    assert client.delete(f"/api/v1/teams/{team_id}").status_code == 403


def test_admin_can_manage_projects_and_members(client):
    """An admin may delete tasks and projects and invite members, but not the team."""
    team_id, project_id, task_id = _team_with_task(client)
    admin = register(client, "admin@example.com", "Admin")
    other = register(client, "other@example.com", "Other")
    extra = register(client, "extra@example.com", "Extra")
    owner_id = client.get("/api/v1/users/me").json()["id"]
    client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": admin["id"], "role": "admin"},
    )
    login_as(client, "admin@example.com")

    assert client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": extra["id"], "role": "admin"},
    ).status_code == 403
    invited = client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": other["id"], "role": "member"},
    )
    assert invited.status_code == 201
    assert client.delete(f"/api/v1/teams/{team_id}/members/{owner_id}").status_code == 403
    assert client.delete(f"/api/v1/teams/{team_id}/members/{admin['id']}").status_code == 403
    assert client.delete(f"/api/v1/tasks/{task_id}").status_code == 204
    assert client.delete(f"/api/v1/projects/{project_id}").status_code == 204
    assert client.delete(f"/api/v1/teams/{team_id}").status_code == 403


def test_outsider_gets_404(client):
    """Someone outside the team cannot tell that the team, project, or task exists."""
    team_id, project_id, task_id = _team_with_task(client)
    register(client, "out@example.com", "Out")
    login_as(client, "out@example.com")

    assert client.get(f"/api/v1/teams/{team_id}").status_code == 404
    assert client.get(f"/api/v1/projects/{project_id}").status_code == 404
    assert client.get(f"/api/v1/tasks/{task_id}").status_code == 404
    listed = client.get("/api/v1/projects").json()
    assert project_id not in [project["id"] for project in listed]
