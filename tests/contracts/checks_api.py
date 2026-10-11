"""Shared JSON API checks (see specs/json-api.md).

Each check assumes a pristine store and a uniform client exposing
``get``/``post``/``patch``/``delete`` returning ``status_code`` + ``json()``.
"""

from typing import Any

OPENAPI_PATHS: dict[str, str] = {
    "fastapi-api-memory": "/openapi.json",
    "fastapi-api-sqlite-sqlalchemy": "/openapi.json",
    "litestar-api-memory": "/schema/openapi.json",
    "litestar-api-sqlite-advanced-alchemy": "/schema/openapi.json",
    "connexion-api-memory": "/openapi.json",
}


def check_list_starts_empty(client: Any) -> None:
    response = client.get("/todos")
    assert response.status_code == 200, response.status_code
    assert response.json() == []


def check_crud_flow(client: Any) -> None:
    created = client.post("/todos", json={"title": "Buy milk"})
    assert created.status_code == 201, created.status_code
    item = created.json()
    assert item["title"] == "Buy milk"
    assert item["done"] is False

    todo_id = item["id"]
    assert client.get(f"/todos/{todo_id}").json() == item

    updated = client.patch(f"/todos/{todo_id}", json={"done": True})
    assert updated.status_code == 200, updated.status_code
    assert updated.json()["done"] is True

    assert client.delete(f"/todos/{todo_id}").status_code == 204
    assert client.get(f"/todos/{todo_id}").status_code == 404


def check_validation_errors(client: Any) -> None:
    for payload in ({"title": ""}, {}):
        response = client.post("/todos", json=payload)
        assert response.status_code == 422, (payload, response.status_code)
        assert response.json() is not None

    created = client.post("/todos", json={"title": "x"}).json()
    bad = client.patch(f"/todos/{created['id']}", json={"title": ""})
    assert bad.status_code == 422, bad.status_code
    assert bad.json() is not None


def check_unknown_id(client: Any) -> None:
    for response in (
        client.get("/todos/9999"),
        client.patch("/todos/9999", json={"done": True}),
        client.delete("/todos/9999"),
    ):
        assert response.status_code == 404, response.status_code
        assert response.json() is not None


def check_openapi(
    client: Any, schema_path: str, item_path: str = "/todos/{todo_id}"
) -> None:
    spec = client.get(schema_path)
    assert spec.status_code == 200, spec.status_code
    paths = spec.json()["paths"]
    assert "/todos" in paths
    assert item_path in paths, sorted(paths)
