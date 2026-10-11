"""Todo JSON API with Twisted Web and in-memory storage."""

import json
import os

from twisted.web.resource import Resource
from twisted.web.server import Request, Site

from .models import Todo
from .repository import InMemoryTodoRepository


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


def _request_body(request: Request) -> dict:
    try:
        raw = request.content.read()
        body = json.loads(raw.decode("utf-8")) if raw else {}
    except (ValueError, UnicodeDecodeError):
        return {}
    return body if isinstance(body, dict) else {}


def _json_response(request: Request, payload: object, status: int = 200) -> bytes:
    request.setHeader(b"Content-Type", b"application/json")
    request.setResponseCode(status)
    return json.dumps(payload).encode("utf-8")


def _not_found(request: Request) -> bytes:
    return _json_response(request, {"error": "Todo not found"}, 404)


class _UnknownResource(Resource):
    """Leaf rendering a JSON 404 for unknown paths."""

    isLeaf = True

    def __init__(self, message: str = "Not found") -> None:
        super().__init__()
        self._message = message

    def render(self, request: Request) -> bytes:
        return _json_response(request, {"error": self._message}, 404)


class TodoItemResource(Resource):
    """Leaf for a single todo item: GET / PATCH / DELETE."""

    isLeaf = True

    def __init__(self, repo: InMemoryTodoRepository, todo_id: int) -> None:
        super().__init__()
        self._repo = repo
        self._todo_id = todo_id

    def render_GET(self, request: Request) -> bytes:
        try:
            todo = self._repo.get(self._todo_id)
        except KeyError:
            return _not_found(request)
        return _json_response(request, _to_json(todo))

    def render_PATCH(self, request: Request) -> bytes:
        body = _request_body(request)
        title = body.get("title")
        done = body.get("done")
        if "title" in body and not _valid_title(title):
            return _json_response(
                request, {"error": "title must be a non-empty string"}, 422
            )
        if done is not None and not isinstance(done, bool):
            return _json_response(request, {"error": "done must be a boolean"}, 422)
        try:
            todo = self._repo.update(self._todo_id, title=title, done=done)
        except KeyError:
            return _not_found(request)
        return _json_response(request, _to_json(todo))

    def render_DELETE(self, request: Request) -> bytes:
        try:
            self._repo.delete(self._todo_id)
        except KeyError:
            return _not_found(request)
        request.setResponseCode(204)
        return b""


class TodosResource(Resource):
    """Collection at /todos: GET (list) / POST (create); children are items."""

    def __init__(self, repo: InMemoryTodoRepository) -> None:
        super().__init__()
        self._repo = repo

    def render_GET(self, request: Request) -> bytes:
        return _json_response(request, [_to_json(todo) for todo in self._repo.list()])

    def render_POST(self, request: Request) -> bytes:
        title = _request_body(request).get("title")
        if not _valid_title(title):
            return _json_response(
                request, {"error": "title must be a non-empty string"}, 422
            )
        return _json_response(request, _to_json(self._repo.create(title=title)), 201)

    def getChild(self, path: bytes, request: Request) -> Resource:
        if path == b"":
            return self
        try:
            todo_id = int(path.decode("ascii"))
        except (ValueError, UnicodeDecodeError):
            return _UnknownResource("Todo not found")
        return TodoItemResource(self._repo, todo_id)


class RootResource(Resource):
    """Root of the resource tree; only /todos is routed."""

    def __init__(self, repo: InMemoryTodoRepository) -> None:
        super().__init__()
        self._todos = TodosResource(repo)

    def getChild(self, path: bytes, request: Request) -> Resource:
        if path == b"":
            return self
        if path == b"todos":
            return self._todos
        return _UnknownResource()

    def render_GET(self, request: Request) -> bytes:
        return _json_response(request, {"error": "Not found"}, 404)


def create_app(repo: InMemoryTodoRepository | None = None) -> Site:
    """Build a fresh Site (resource tree + store) per call."""
    repo = repo or InMemoryTodoRepository()
    return Site(RootResource(repo))


app = create_app()


def main() -> None:
    from twisted.internet import reactor

    port = int(os.environ.get("PORT", "8000"))
    reactor.listenTCP(port, create_app())
    reactor.run()


if __name__ == "__main__":
    main()
