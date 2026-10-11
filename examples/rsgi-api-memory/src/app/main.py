"""Bare RSGI todo JSON API served by Granian.

RSGI callable shape (see https://github.com/emmett-framework/granian/blob/master/docs/spec/RSGI.md):

    async def app(scope, protocol): ...

- ``scope``: HTTP connection scope (``method``, ``path``, ``headers``, ...).
- ``protocol``: await ``protocol()`` for the full request body (bytes);
  respond via ``protocol.response_str/response_bytes/response_empty``.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Awaitable, Callable
from typing import Any

from .repository import InMemoryTodoRepository

repo = InMemoryTodoRepository()

_TODOS_RE = re.compile(r"^/todos$")
_TODO_RE = re.compile(r"^/todos/([^/]+)$")

JSON_HEADERS = [("content-type", "application/json")]


def _json_response(protocol: Any, status: int, payload: Any) -> None:
    protocol.response_str(status, JSON_HEADERS, json.dumps(payload))


def _error(protocol: Any, status: int, message: str) -> None:
    _json_response(protocol, status, {"detail": message})


def _parse_id(raw: str) -> int | None:
    try:
        value = int(raw)
    except ValueError:
        return None
    return value


def _validate_title(data: Any) -> str | None:
    """Return an error message, or None when the title is valid."""
    if not isinstance(data, dict):
        return "Invalid JSON body"
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return "Title must be a non-empty string"
    return None


async def _read_json(protocol: Any) -> tuple[Any, str | None]:
    try:
        body = await protocol()
    except Exception:
        return None, "Could not read request body"
    if not body:
        return None, "Empty request body"
    try:
        return json.loads(body.decode("utf-8")), None
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "Invalid JSON body"


async def app(scope: Any, protocol: Any) -> None:
    if getattr(scope, "proto", "http") != "http":
        _error(protocol, 500, "Unsupported protocol")
        return

    method = scope.method.upper()
    path = scope.path

    if _TODOS_RE.match(path):
        if method == "GET":
            _json_response(protocol, 200, [t.to_dict() for t in repo.list()])
            return
        if method == "POST":
            data, err = await _read_json(protocol)
            if err is not None:
                _error(protocol, 422, err)
                return
            title_err = _validate_title(data)
            if title_err is not None:
                _error(protocol, 422, title_err)
                return
            todo = repo.create(title=data["title"].strip())
            _json_response(protocol, 201, todo.to_dict())
            return
        _error(protocol, 404, "Not found")
        return

    match = _TODO_RE.match(path)
    if match:
        todo_id = _parse_id(match.group(1))
        if todo_id is None:
            _error(protocol, 404, "Todo not found")
            return
        if method == "GET":
            try:
                todo = repo.get(todo_id)
            except KeyError:
                _error(protocol, 404, "Todo not found")
                return
            _json_response(protocol, 200, todo.to_dict())
            return
        if method == "PATCH":
            data, err = await _read_json(protocol)
            if err is not None:
                _error(protocol, 422, err)
                return
            if not isinstance(data, dict) or (
                "title" not in data and "done" not in data
            ):
                _error(protocol, 422, "Nothing to update")
                return
            title: str | None = None
            done: bool | None = None
            if "title" in data:
                if not isinstance(data["title"], str) or not data["title"].strip():
                    _error(protocol, 422, "Title must be a non-empty string")
                    return
                title = data["title"].strip()
            if "done" in data:
                if not isinstance(data["done"], bool):
                    _error(protocol, 422, "Done must be a boolean")
                    return
                done = data["done"]
            try:
                todo = repo.update(todo_id, title=title, done=done)
            except KeyError:
                _error(protocol, 404, "Todo not found")
                return
            _json_response(protocol, 200, todo.to_dict())
            return
        if method == "DELETE":
            try:
                repo.delete(todo_id)
            except KeyError:
                _error(protocol, 404, "Todo not found")
                return
            protocol.response_empty(204, [])
            return
        _error(protocol, 404, "Not found")
        return

    _error(protocol, 404, "Not found")


def reset_store() -> None:
    """Test/harness hook: clear the process-local in-memory store."""
    repo.reset()


def create_app(
    repository: InMemoryTodoRepository | None = None,
) -> Callable[[Any], Awaitable[None]]:
    """Factory equivalent: swap the module-level store and return the RSGI callable.

    Bare RSGI has no app-object idiom; the callable closes over module state,
    so tests/harness reset via ``reset_store()`` (or pass a repository whose
    contents replace the current store).
    """
    global repo
    if repository is not None:
        repo = repository
    else:
        repo = InMemoryTodoRepository()
    return app


def main() -> None:
    import sys

    from granian import Granian

    port = int(os.environ.get("PORT", "8000"))
    target = "app.main:app"
    # Allow running both from the example dir (src layout on sys.path via
    # `uv run --project`) and from the repo root. Resolve the src dir from
    # __file__ so the default never depends on cwd.
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    server = Granian(target, interface="rsgi", address="0.0.0.0", port=port)
    server.serve()


if __name__ == "__main__":
    main()
