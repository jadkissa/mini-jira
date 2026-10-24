def test_create_project(client):
    response = client.post(
        "/api/v1/projects",
        json={"name": "Demo", "description": "First project"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Demo"
    assert "id" in body


def test_get_missing_project(client):
    response = client.get("/api/v1/projects/999")

    assert response.status_code == 404