from datetime import datetime, timedelta, UTC

def test_create_task(client):
    """Creating a task under a project returns 201 and that project id."""
    project = client.post("/api/v1/projects", json={"name": "Demo"})
    project_id = project.json()["id"]

    response = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "First task", "description": "Demo"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "First task"
    assert body["project_id"] == project_id


def test_get_missing_task(client):
    """Fetching an unknown task returns 404."""
    response = client.get("/api/v1/tasks/999")

    assert response.status_code == 404

def test_list_tasks_only_for_that_project(client):
    """Listing tasks returns only the tasks that belong to that project."""
    first = client.post("/api/v1/projects", json={"name": "First"}).json()
    second = client.post("/api/v1/projects", json={"name": "Second"}).json()

    client.post(f"/api/v1/projects/{first['id']}/tasks", json={"title": "A"})
    client.post(f"/api/v1/projects/{first['id']}/tasks", json={"title": "B"})
    client.post(f"/api/v1/projects/{second['id']}/tasks", json={"title": "C"})

    response = client.get(f"/api/v1/projects/{first['id']}/tasks")

    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["A", "B"]


def test_create_task_sets_delivery_date(client):
    """Creating a task with duration_days sets delivery_date that many days ahead."""
    project_id = client.post("/api/v1/projects", json={"name": "Demo"}).json()["id"]

    response = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Ship it", "duration_days": 5},
    )

    assert response.status_code == 201
    expected = (datetime.now(UTC).date() + timedelta(days=5)).isoformat()
    assert response.json()["delivery_date"] == expected