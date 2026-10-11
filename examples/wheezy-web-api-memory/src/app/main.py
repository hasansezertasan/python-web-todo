"""Todo JSON API with wheezy.web and in-memory storage."""

import json
import os

from wheezy.http import (
    HTTPRequest,
    HTTPResponse,
    WSGIApplication,
    json_response,
    method_not_allowed,
)
from wheezy.http.response import HTTP_STATUS
from wheezy.routing import url
from wheezy.web.handlers import MethodHandler
from wheezy.web.middleware import bootstrap_defaults, path_routing_middleware_factory

from .models import Todo
from .repository import InMemoryTodoRepository

# wheezy.http ships no 422 status; register the standard RFC 9110 reason
# phrase so validation errors satisfy the contract (remapped in-example,
# per repo convention).
HTTP_STATUS.setdefault(422, "422 Unprocessable Entity")


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


def _json(payload: object, status: int = 200) -> HTTPResponse:
    response = json_response(payload)
    response.status_code = status
    return response


def _error(message: str, status: int) -> HTTPResponse:
    return _json({"error": message}, status)


def _request_body(request: HTTPRequest) -> dict:
    try:
        length = int(request.environ.get("CONTENT_LENGTH") or 0)
    except (TypeError, ValueError):
        return {}
    if length <= 0:
        return {}
    try:
        body = json.loads(request.environ["wsgi.input"].read(length).decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return {}
    return body if isinstance(body, dict) else {}


def _todo_id(route_args: dict) -> int | None:
    try:
        return int(route_args["todo_id"])
    except (KeyError, TypeError, ValueError):
        return None


class TodosHandler(MethodHandler):
    """Collection handler for GET/POST /todos."""

    @property
    def repo(self) -> InMemoryTodoRepository:
        return self.options["todo_repo"]

    def get(self) -> HTTPResponse:
        return _json([_to_json(todo) for todo in self.repo.list()])

    def post(self) -> HTTPResponse:
        title = _request_body(self.request).get("title")
        if not _valid_title(title):
            return _error("title must be a non-empty string", 422)
        return _json(_to_json(self.repo.create(title=title)), 201)


class TodoItemHandler(MethodHandler):
    """Item handler for GET/PATCH/DELETE /todos/{id}.

    MethodHandler only dispatches GET/POST/HEAD, so dispatch is extended
    here to cover PATCH and DELETE.
    """

    @property
    def repo(self) -> InMemoryTodoRepository:
        return self.options["todo_repo"]

    def __call__(self) -> HTTPResponse:
        method = self.request.method
        if method == "GET":
            response = self.get()
        elif method == "PATCH":
            response = self.patch()
        elif method == "DELETE":
            response = self.delete()
        else:
            response = method_not_allowed()
        if self.cookies:
            response.cookies.extend(self.cookies)
        return response

    def get(self) -> HTTPResponse:
        todo_id = _todo_id(self.route_args)
        if todo_id is None:
            return _error("Todo not found", 404)
        try:
            todo = self.repo.get(todo_id)
        except KeyError:
            return _error("Todo not found", 404)
        return _json(_to_json(todo))

    def patch(self) -> HTTPResponse:
        todo_id = _todo_id(self.route_args)
        if todo_id is None:
            return _error("Todo not found", 404)
        body = _request_body(self.request)
        title = body.get("title")
        done = body.get("done")
        if title is not None and not _valid_title(title):
            return _error("title must be a non-empty string", 422)
        if done is not None and not isinstance(done, bool):
            return _error("done must be a boolean", 422)
        try:
            todo = self.repo.update(todo_id, title=title, done=done)
        except KeyError:
            return _error("Todo not found", 404)
        return _json(_to_json(todo))

    def delete(self) -> HTTPResponse:
        todo_id = _todo_id(self.route_args)
        if todo_id is None:
            return _error("Todo not found", 404)
        try:
            self.repo.delete(todo_id)
        except KeyError:
            return _error("Todo not found", 404)
        response = HTTPResponse()
        response.status_code = 204
        # A 204 carries no body, so drop the default Content-Type header.
        response.headers = [
            header for header in response.headers if header[0] != "Content-Type"
        ]
        return response


all_urls = [
    url("todos", TodosHandler, name="todos"),
    url("todos/{todo_id}", TodoItemHandler, name="todo"),
]


def create_app(repo: InMemoryTodoRepository | None = None) -> WSGIApplication:
    repo = repo or InMemoryTodoRepository()
    options = {
        "todo_repo": repo,
        # API-only example: no template rendering; silences the bootstrap
        # warning that render_template is not defined.
        "render_template": None,
    }
    return WSGIApplication(
        middleware=[
            bootstrap_defaults(url_mapping=all_urls),
            path_routing_middleware_factory,
        ],
        options=options,
    )


app = create_app()


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    from wsgiref.simple_server import make_server

    with make_server("0.0.0.0", port, app) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
