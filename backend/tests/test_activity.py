from tests.helpers import create_project, login_as, register


def test_activity_records_create_update_and_comment(client):
    """Creating, editing, and commenting on a task each leave an activity row."""
    project_id = create_project(client, "Demo").json()["id"]
    task_id = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "First"},
    ).json()["id"]
    client.patch(f"/api/v1/tasks/{task_id}", json={"status": "done"})
    client.post(f"/api/v1/tasks/{task_id}/comments", json={"body": "Ship it"})

    rows = client.get(f"/api/v1/tasks/{task_id}/activity").json()
    assert [row["action"] for row in rows] == ["created", "status", "commented"]
    assert rows[1]["old_value"] == "todo"
    assert rows[1]["new_value"] == "done"
    assert rows[2]["new_value"] == "Ship it"


def test_outsider_cannot_read_activity(client):
    """Someone outside the team gets 404 for the task's activity."""
    project_id = create_project(client, "Demo").json()["id"]
    task_id = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "First"},
    ).json()["id"]
    register(client, "out@example.com", "Out")
    login_as(client, "out@example.com")
    assert client.get(f"/api/v1/tasks/{task_id}/activity").status_code == 404
