"""Todo JSON API with circuits.web and in-memory storage.

circuits.web idioms used here: a ``Controller`` subclass bound to the
``/todos`` channel, with one handler per HTTP verb. The ``Controller``
metaclass auto-exposes each public method as the event of the same name,
and the default ``Dispatcher`` routes ``GET``/``POST``/``PATCH``/``DELETE``
requests on this channel to the matching verb handler, passing any extra
path segments (the todo id) as positional arguments.
"""

import json
from typing import Any

from circuits.web import Controller

from .models import Todo
from .repository import InMemoryTodoRepository


def _to_dict(todo: Todo) -> dict[str, Any]:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


class TodosController(Controller):
    channel = "/todos"

    def __init__(self, repo: InMemoryTodoRepository | None = None) -> None:
        super().__init__()
        self._repo = repo or InMemoryTodoRepository()

    def _json(self, data: Any, status: int = 200) -> str:
        self.response.status = status
        self.response.headers["Content-Type"] = "application/json"
        return json.dumps(data)

    def _not_found(self) -> str:
        return self._json({"detail": "Todo not found"}, 404)

    def _invalid_title(self) -> str:
        return self._json({"detail": "Title must not be empty"}, 422)

    def _read_payload(self) -> Any:
        try:
            raw = self.request.body.getvalue().decode("utf-8")
        except (AttributeError, UnicodeDecodeError):
            return None
        if not raw.strip():
            return None
        try:
            return json.loads(raw)
        except ValueError:
            return None

    def _todo_id(self, todo_id: str | None) -> int | None:
        try:
            return int(todo_id)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return None

    def GET(self, todo_id: str | None = None, **kwargs: Any) -> str:
        if todo_id is None:
            return self._json([_to_dict(todo) for todo in self._repo.list()])
        parsed = self._todo_id(todo_id)
        if parsed is None:
            return self._not_found()
        try:
            return self._json(_to_dict(self._repo.get(parsed)))
        except KeyError:
            return self._not_found()

    def POST(self, **kwargs: Any) -> str:
        payload = self._read_payload()
        title = payload.get("title") if isinstance(payload, dict) else None
        if not isinstance(title, str) or len(title) < 1:
            return self._invalid_title()
        return self._json(_to_dict(self._repo.create(title)), 201)

    def PATCH(self, todo_id: str | None = None, **kwargs: Any) -> str:
        parsed = self._todo_id(todo_id)
        if parsed is None:
            return self._not_found()
        try:
            self._repo.get(parsed)
        except KeyError:
            return self._not_found()
        payload = self._read_payload()
        if not isinstance(payload, dict):
            payload = {}
        title = payload.get("title")
        done = payload.get("done")
        if title is not None and (not isinstance(title, str) or len(title) < 1):
            return self._invalid_title()
        if done is not None:
            done = bool(done)
        return self._json(_to_dict(self._repo.update(parsed, title=title, done=done)))

    def DELETE(self, todo_id: str | None = None, **kwargs: Any) -> str:
        parsed = self._todo_id(todo_id)
        if parsed is None:
            return self._not_found()
        try:
            self._repo.delete(parsed)
        except KeyError:
            return self._not_found()
        self.response.status = 204
        self.response.headers["Content-Type"] = "application/json"
        return ""
