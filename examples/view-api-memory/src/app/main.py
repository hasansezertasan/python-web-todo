"""Todo JSON API with view.py and in-memory storage."""

import os

from view.core.app import App
from view.core.headers import HTTPHeaders
from view.core.request import Request
from view.core.response import Response
from view.responses import JSONResponse

from .models import Todo
from .repository import InMemoryTodoRepository

# NOTE: responses intentionally carry no headers. view.py's ASGI sender
# (view.run.asgi.asgi_for_app -> headers_to_asgi) iterates the header map
# instead of its items, so any response with headers raises
# "ValueError: too many values to unpack" and becomes a 500 over real HTTP.
# Bodies are still JSON; clients parse them without a content-type.


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


async def _read_body(request: Request) -> dict:
    try:
        data = await request.json()
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _not_found() -> JSONResponse:
    return JSONResponse.from_content({"detail": "Todo not found"}, status_code=404)


def _invalid_title() -> JSONResponse:
    return JSONResponse.from_content(
        {"detail": "title must be a non-empty string"}, status_code=422
    )


def _invalid_done() -> JSONResponse:
    return JSONResponse.from_content(
        {"detail": "done must be a boolean"}, status_code=422
    )


def _parse_id(request: Request) -> int | None:
    try:
        return int(request.path_parameters["todo_id"])
    except (KeyError, TypeError, ValueError):
        return None


def _no_content() -> Response:
    async def _empty():
        return
        yield b""  # pragma: no cover

    return Response(receive_data=_empty(), status_code=204, headers=HTTPHeaders())


def create_app(repo: InMemoryTodoRepository | None = None) -> App:
    repo = repo or InMemoryTodoRepository()
    app = App()

    @app.get("/todos")
    async def list_todos():
        return JSONResponse.from_content([_to_json(todo) for todo in repo.list()])

    @app.post("/todos")
    async def create_todo():
        body = await _read_body(app.current_request())
        title = body.get("title")
        if not _valid_title(title):
            return _invalid_title()
        return JSONResponse.from_content(
            _to_json(repo.create(title=title)), status_code=201
        )

    @app.get("/todos/{todo_id}")
    async def get_todo():
        todo_id = _parse_id(app.current_request())
        if todo_id is None:
            return _not_found()
        try:
            return JSONResponse.from_content(_to_json(repo.get(todo_id)))
        except KeyError:
            return _not_found()

    @app.patch("/todos/{todo_id}")
    async def update_todo():
        request = app.current_request()
        todo_id = _parse_id(request)
        if todo_id is None:
            return _not_found()
        body = await _read_body(request)
        title = body.get("title")
        done = body.get("done")
        if title is not None and not _valid_title(title):
            return _invalid_title()
        if done is not None and not isinstance(done, bool):
            return _invalid_done()
        try:
            return JSONResponse.from_content(
                _to_json(repo.update(todo_id, title=title, done=done))
            )
        except KeyError:
            return _not_found()

    @app.delete("/todos/{todo_id}")
    async def delete_todo():
        todo_id = _parse_id(app.current_request())
        if todo_id is None:
            return _not_found()
        try:
            repo.delete(todo_id)
        except KeyError:
            return _not_found()
        return _no_content()

    return app


app = create_app()


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
