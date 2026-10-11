"""Shared server-rendered checks (see specs/server-rendered.md).

Each check assumes a pristine store and a uniform client exposing
``get``/``post`` returning ``status_code`` + ``text``. POSTs may answer
with the final page (200, client followed the redirect) or with the
redirect itself (302/303), so checks assert the status loosely and then
verify state with a fresh GET.
"""

from typing import Any

REDIRECTS = {200, 302, 303}
REJECTED = {200, 400, 422}


def check_list_page(client: Any) -> None:
    response = client.get("/")
    assert response.status_code == 200, response.status_code
    page = response.text
    assert "Todo List" in page
    assert "No todos yet." in page
    assert 'name="title"' in page


def check_add_flow(client: Any) -> None:
    response = client.post("/todos", data={"title": "Buy milk"})
    assert response.status_code in REDIRECTS, response.status_code
    page = client.get("/").text
    assert "Buy milk" in page
    assert "not done" in page
    assert ">Mark done<" in page


def check_toggle_flow(client: Any) -> None:
    client.post("/todos", data={"title": "Buy milk"})
    response = client.post("/todos/1/toggle")
    assert response.status_code in REDIRECTS, response.status_code
    page = client.get("/").text
    assert ">Mark not done<" in page
    assert ">Mark done<" not in page


def check_delete_flow(client: Any) -> None:
    client.post("/todos", data={"title": "Buy milk"})
    response = client.post("/todos/1/delete")
    assert response.status_code in REDIRECTS, response.status_code
    page = client.get("/").text
    assert "Buy milk" not in page
    assert "No todos yet." in page


def check_empty_title_rejected(client: Any) -> None:
    response = client.post("/todos", data={"title": ""})
    assert response.status_code in REJECTED, response.status_code
    assert "Title must not be empty" in response.text
    assert "No todos yet." in client.get("/").text


def check_unknown_id(client: Any) -> None:
    assert client.post("/todos/999/toggle").status_code == 404
    assert client.post("/todos/999/delete").status_code == 404
