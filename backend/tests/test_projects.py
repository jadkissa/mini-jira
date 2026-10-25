def test_create_project(client):
    """Creating a project returns 201 and the saved name."""
    response = client.post(
        "/api/v1/projects",
        json={"name": "Demo", "description": "First project"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Demo"
    assert "id" in body


def test_get_missing_project(client):
    """Fetching an unknown project returns 404."""
    response = client.get("/api/v1/projects/999")

    assert response.status_code == 404

def test_delete_missing_project(client):
    """Deleting an unknown project returns 404."""
    response = client.delete("/api/v1/projects/999")
    assert response.status_code == 404


def test_list_projects_is_paginated(client):
    """Listing projects returns only the requested page size."""
    for name in ("A", "B", "C"):
        client.post("/api/v1/projects", json={"name": name})

    response = client.get("/api/v1/projects?page=1&page_size=2")

    assert response.status_code == 200
    assert len(response.json()) == 2