"""View functions wired to ``openapi.yaml`` via ``operationId`` (OpenAPI-first).

Connexion resolves each ``operationId`` (``app.handlers.*``) to a module-level
function here. The functions read the module-level ``store``, which
:func:`app.main.create_app` swaps out so every factory call starts fresh.
"""

from __future__ import annotations

from typing import Any

from connexion import problem

from .repository import InMemoryTodoRepository

store: InMemoryTodoRepository = InMemoryTodoRepository()


def use_store(repo: InMemoryTodoRepository) -> None:
    """Bind the handlers to ``repo`` (used by ``create_app`` for fresh state)."""
    global store  # noqa: PLW0603 — operationId handlers share module state by design
    store = repo


def _item(todo: Any) -> dict[str, Any]:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _not_found(todo_id: int) -> Any:
    return problem(status=404, title="Not Found", detail=f"Todo {todo_id} not found.")


def _invalid_title() -> Any:
    return problem(
        status=422,
        title="Unprocessable Entity",
        detail="Title must be a non-empty string.",
    )


def _invalid_done() -> Any:
    return problem(
        status=422, title="Unprocessable Entity", detail="Done must be a boolean."
    )


def _valid_title(value: Any) -> bool:
    return isinstance(value, str) and len(value) > 0


def list_todos() -> list[dict[str, Any]]:
    return [_item(todo) for todo in store.list()]


def create_todo(body: Any) -> Any:
    title = body.get("title") if isinstance(body, dict) else None
    if not _valid_title(title):
        return _invalid_title()
    return _item(store.create(title=title)), 201


def get_todo(todo_id: int) -> Any:
    try:
        return _item(store.get(todo_id))
    except KeyError:
        return _not_found(todo_id)


def update_todo(todo_id: int, body: Any) -> Any:
    data = body if isinstance(body, dict) else {}
    if "title" in data:
        if not _valid_title(data["title"]):
            return _invalid_title()
        title = data["title"]
    else:
        title = None
    done = data.get("done")
    if done is not None and not isinstance(done, bool):
        return _invalid_done()
    try:
        return _item(store.update(todo_id, title=title, done=done))
    except KeyError:
        return _not_found(todo_id)


def delete_todo(todo_id: int) -> Any:
    try:
        store.delete(todo_id)
    except KeyError:
        return _not_found(todo_id)
    return None, 204
