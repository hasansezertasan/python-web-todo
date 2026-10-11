"""Todo JSON API with Quixote and in-memory storage.

Quixote idioms used here: a ``Publisher`` rooted at a ``Directory`` tree,
URL dispatch via ``Directory._q_traverse``/``_q_lookup``, per-request access
through ``quixote.get_request()``/``quixote.get_response()``, and the stock
``QWIP`` adapter to expose the publisher as a WSGI application.
"""

import json
import os
from collections.abc import Callable
from typing import ClassVar
from wsgiref.simple_server import make_server

import quixote
from quixote.directory import Directory
from quixote.publish import Publisher
from quixote.wsgi import QWIP

from .models import Todo
from .repository import InMemoryTodoRepository


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


def _json_response(payload: dict | list, status: int = 200) -> str:
    """Set the JSON content type + status on the Quixote response; the
    returned string becomes the response body."""
    response = quixote.get_response()
    response.set_content_type("application/json")
    response.set_status(status)
    return json.dumps(payload)


def _read_json_body() -> dict:
    """Read the request body as a JSON object.

    Quixote only parses urlencoded/multipart bodies into ``request.form``;
    for ``application/json`` the buffered raw body is read from stdin.
    Unparseable bodies are treated as an empty object so validation
    reports them as a missing title (422) per the contract.
    """
    request = quixote.get_request()
    raw = request.stdin.read()
    if not raw:
        return {}
    try:
        data = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _not_found() -> str:
    return _json_response({"error": "Todo not found"}, status=404)


class TodosDirectory(Directory):
    """Serves the ``/todos`` collection and every ``/todos/{id}`` item.

    Quixote traversal calls this object with no remaining path for bare
    ``/todos`` (``__call__``) and routes each extra path component through
    ``_q_lookup``. Method dispatch is on ``request.get_method()`` — Quixote
    has no per-method routing of its own.
    """

    _q_exports: ClassVar[list] = []

    def __init__(self, repo: InMemoryTodoRepository) -> None:
        self._repo = repo

    def __call__(self) -> str:
        # Bare /todos (no trailing slash): serve the collection directly
        # instead of Quixote's stock redirect-to-trailing-slash.
        return self._collection()

    def _q_lookup(self, component: str) -> Callable[[], str]:
        if component == "":
            # Trailing slash (/todos/): the same collection resource.
            return self._collection
        # Any other single component is treated as an item id; unknown or
        # non-integer ids answer 404 with a JSON body per the contract.
        return lambda: self._item(component)

    def _collection(self) -> str:
        method = quixote.get_request().get_method()
        if method == "GET":
            return _json_response([_to_json(todo) for todo in self._repo.list()])
        if method == "POST":
            title = _read_json_body().get("title")
            if not _valid_title(title):
                return _json_response(
                    {"error": "title must be a non-empty string"}, status=422
                )
            return _json_response(_to_json(self._repo.create(title=title)), status=201)
        return _json_response({"error": "Method not allowed"}, status=405)

    def _item(  # noqa: PLR0911 — method dispatch branches per verb
        self, raw_id: str
    ) -> str:
        try:
            todo_id = int(raw_id)
        except (TypeError, ValueError):
            return _not_found()
        method = quixote.get_request().get_method()
        if method == "GET":
            try:
                return _json_response(_to_json(self._repo.get(todo_id)))
            except KeyError:
                return _not_found()
        if method == "PATCH":
            body = _read_json_body()
            title = body.get("title")
            done = body.get("done")
            if title is not None and not _valid_title(title):
                return _json_response(
                    {"error": "title must be a non-empty string"}, status=422
                )
            try:
                return _json_response(
                    _to_json(self._repo.update(todo_id, title=title, done=done))
                )
            except KeyError:
                return _not_found()
        if method == "DELETE":
            try:
                self._repo.delete(todo_id)
            except KeyError:
                return _not_found()
            quixote.get_response().set_status(204)
            # Explicit zero length: with no body Quixote would otherwise emit
            # "Connection: close", which wsgiref rejects as hop-by-hop.
            quixote.get_response().set_header("Content-Length", "0")
            return ""
        return _json_response({"error": "Method not allowed"}, status=405)


class RootDirectory(Directory):
    _q_exports: ClassVar[list] = ["todos"]

    def __init__(self, repo: InMemoryTodoRepository) -> None:
        self.todos = TodosDirectory(repo)


def create_app(repo: InMemoryTodoRepository | None = None) -> QWIP:
    """Return a fresh WSGI app with its own empty store (unless given).

    The ``QWIP`` adapter wraps the Quixote ``Publisher`` so the app works
    with any WSGI server or in-process WSGI test client (e.g. webtest).
    """
    root = RootDirectory(repo or InMemoryTodoRepository())
    try:
        publisher = Publisher(root)
    except RuntimeError:
        # Quixote allows only one Publisher per process: reuse it and swap
        # in a fresh root directory so every factory call still gets an
        # isolated (freshly seeded) store in long-lived processes.
        publisher = quixote.get_publisher()
        publisher.root_directory = root
    # Stock Quixote only allows GET/HEAD/POST; the contract needs PATCH
    # and DELETE on /todos/{id} too.
    publisher.config.allowed_methods = [
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ]
    # The store is lock-protected, so the publisher is safe behind
    # multi-threaded WSGI servers/clients (QWIP asserts otherwise).
    publisher.is_thread_safe = True
    return QWIP(publisher)


app = create_app()


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    with make_server("0.0.0.0", port, app) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
