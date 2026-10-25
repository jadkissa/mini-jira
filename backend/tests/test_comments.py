from tests.helpers import create_project, login_as, register


def _task(client):
    project_id = create_project(client, "Demo").json()["id"]
    task_id = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "First"},
    ).json()["id"]
    return project_id, task_id


def test_create_and_list_comments(client):
    """A member can add a comment and read it back."""
    _, task_id = _task(client)

    created = client.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"body": "Looks good"},
    )
    assert created.status_code == 201
    assert created.json()["body"] == "Looks good"
    assert created.json()["author_id"] == client.get("/api/v1/users/me").json()["id"]

    listed = client.get(f"/api/v1/tasks/{task_id}/comments")
    assert listed.status_code == 200
    assert [row["body"] for row in listed.json()] == ["Looks good"]


def test_comment_list_is_paginated(client):
    """Comment lists return only the requested page size."""
    _, task_id = _task(client)
    for body in ("A", "B", "C"):
        client.post(f"/api/v1/tasks/{task_id}/comments", json={"body": body})

    response = client.get(f"/api/v1/tasks/{task_id}/comments?page=1&page_size=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_empty_comment_is_rejected(client):
    """A blank comment is a validation error."""
    _, task_id = _task(client)
    response = client.post(f"/api/v1/tasks/{task_id}/comments", json={"body": ""})
    assert response.status_code == 422


def test_outsider_cannot_see_comments(client):
    """Someone outside the team gets 404 for the task's comments."""
    _, task_id = _task(client)
    register(client, "out@example.com", "Out")
    login_as(client, "out@example.com")
    assert client.get(f"/api/v1/tasks/{task_id}/comments").status_code == 404
