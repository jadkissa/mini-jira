from tests.helpers import create_project, login_as, register


def _project_and_task(client):
    project_id = create_project(client, "Demo").json()["id"]
    task_id = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "First"},
    ).json()["id"]
    return project_id, task_id


def test_manager_creates_label_and_member_attaches_it(client):
    """Owners create labels. Members can attach and remove them on a task."""
    project_id, task_id = _project_and_task(client)
    created = client.post(
        f"/api/v1/projects/{project_id}/labels",
        json={"name": "bug", "color": "red"},
    )
    assert created.status_code == 201
    label_id = created.json()["id"]

    member = register(client, "member@example.com", "Member")
    team_id = client.get(f"/api/v1/projects/{project_id}").json()["team_id"]
    client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"user_id": member["id"], "role": "member"},
    )
    login_as(client, "member@example.com")

    assert client.post(
        f"/api/v1/projects/{project_id}/labels",
        json={"name": "feature"},
    ).status_code == 403
    assert client.get(f"/api/v1/projects/{project_id}/labels").status_code == 200

    attached = client.post(
        f"/api/v1/tasks/{task_id}/labels",
        json={"label_id": label_id},
    )
    assert attached.status_code == 201
    assert client.get(f"/api/v1/tasks/{task_id}/labels").json()[0]["name"] == "bug"
    assert client.delete(f"/api/v1/tasks/{task_id}/labels/{label_id}").status_code == 204
    assert client.get(f"/api/v1/tasks/{task_id}/labels").json() == []


def test_duplicate_label_name_is_rejected(client):
    """A project cannot have two labels with the same name."""
    project_id, _ = _project_and_task(client)
    client.post(f"/api/v1/projects/{project_id}/labels", json={"name": "bug"})
    again = client.post(f"/api/v1/projects/{project_id}/labels", json={"name": "bug"})
    assert again.status_code == 409


def test_cannot_attach_a_label_from_another_project(client):
    """A label belongs to one project and cannot be put on another project's task."""
    project_id, _ = _project_and_task(client)
    other_id = create_project(client, "Other").json()["id"]
    other_task = client.post(
        f"/api/v1/projects/{other_id}/tasks",
        json={"title": "Elsewhere"},
    ).json()["id"]
    label_id = client.post(
        f"/api/v1/projects/{project_id}/labels",
        json={"name": "bug"},
    ).json()["id"]

    response = client.post(
        f"/api/v1/tasks/{other_task}/labels",
        json={"label_id": label_id},
    )
    assert response.status_code == 404


def test_outsider_cannot_list_labels(client):
    """Someone outside the team gets 404 for the project's labels."""
    project_id, _ = _project_and_task(client)
    register(client, "out@example.com", "Out")
    login_as(client, "out@example.com")
    assert client.get(f"/api/v1/projects/{project_id}/labels").status_code == 404
