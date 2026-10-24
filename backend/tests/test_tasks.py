def test_create_task(client):
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
    response = client.get("/api/v1/tasks/999")

    assert response.status_code == 404