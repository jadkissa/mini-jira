from datetime import datetime, timedelta, UTC

from tests.helpers import create_project

def test_create_task(client):
    """Creating a task under a project returns 201 and that project id."""
    project = create_project(client, "Demo")
    project_id = project.json()["id"]

    response = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "First task", "description": "Demo"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "First task"
    assert body["project_id"] == project_id
    assert body["reporter_id"] == client.get("/api/v1/users/me").json()["id"]
    assert body["assignee_id"] is None


def test_create_task_can_set_assignee(client):
    """assignee_id is stored when that user exists."""
    project_id = create_project(client, "Demo").json()["id"]
    assignee = client.post(
        "/api/v1/users",
        json={"email": "bob@example.com", "password": "secret", "full_name": "Bob"},
    ).json()

    response = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Assigned", "assignee_id": assignee["id"]},
    )

    assert response.status_code == 201
    assert response.json()["assignee_id"] == assignee["id"]


def test_create_task_rejects_missing_assignee(client):
    """An unknown assignee returns 404."""
    project_id = create_project(client, "Demo").json()["id"]

    response = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Missing", "assignee_id": 99999},
    )

    assert response.status_code == 404


def test_get_missing_task(client):
    """Fetching an unknown task returns 404."""
    response = client.get("/api/v1/tasks/999")

    assert response.status_code == 404

def test_list_tasks_only_for_that_project(client):
    """Listing tasks returns only the tasks that belong to that project."""
    first = create_project(client, "First").json()
    second = create_project(client, "Second").json()

    client.post(f"/api/v1/projects/{first['id']}/tasks", json={"title": "A"})
    client.post(f"/api/v1/projects/{first['id']}/tasks", json={"title": "B"})
    client.post(f"/api/v1/projects/{second['id']}/tasks", json={"title": "C"})

    response = client.get(f"/api/v1/projects/{first['id']}/tasks")

    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["A", "B"]


def test_create_task_sets_delivery_date(client):
    """Creating a task with duration_days sets delivery_date that many days ahead."""
    project_id = create_project(client, "Demo").json()["id"]

    response = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Ship it", "duration_days": 5},
    )

    assert response.status_code == 201
    expected = (datetime.now(UTC).date() + timedelta(days=5)).isoformat()
    assert response.json()["delivery_date"] == expected


def test_list_tasks_filters_by_status(client):
    """Listing tasks with status returns only tasks in that status."""
    project_id = create_project(client, "Demo").json()["id"]
    client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "A", "status": "todo"},
    )
    client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "B", "status": "done"},
    )

    response = client.get(f"/api/v1/projects/{project_id}/tasks?status=todo")

    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["A"]


def test_list_tasks_sorts_by_delivery_date(client):
    """sort=delivery_date returns the earlier delivery date first."""
    project_id = create_project(client, "Demo").json()["id"]
    client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Later", "duration_days": 10},
    )
    client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Sooner", "duration_days": 1},
    )

    response = client.get(f"/api/v1/projects/{project_id}/tasks?sort=delivery_date")

    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    assert titles == ["Sooner", "Later"]


def test_list_tasks_rejects_unknown_sort(client):
    """An unknown sort field returns 422."""
    project_id = create_project(client, "Demo").json()["id"]

    response = client.get(f"/api/v1/projects/{project_id}/tasks?sort=nope")

    assert response.status_code == 422