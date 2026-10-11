"""Todo JSON API with Baize (ASGI) and in-memory storage."""

import json
import os
from typing import TypeGuard

from baize.asgi import JSONResponse, Request, Response, Router, request_response

from .models import Todo
from .repository import InMemoryTodoRepository


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> TypeGuard[str]:
    return isinstance(value, str) and len(value) > 0


async def _read_body(request: Request) -> dict:
    try:
        data = json.loads((await request.body).decode("utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _not_found() -> JSONResponse:
    return JSONResponse({"detail": "Todo not found"}, status_code=404)


def _invalid_title() -> JSONResponse:
    return JSONResponse({"detail": "title must be a non-empty string"}, status_code=422)


def _invalid_done() -> JSONResponse:
    return JSONResponse({"detail": "done must be a boolean"}, status_code=422)


def _method_not_allowed() -> JSONResponse:
    return JSONResponse({"detail": "Method not allowed"}, status_code=405)


def create_app(repo: InMemoryTodoRepository | None = None) -> Router:
    store = repo or InMemoryTodoRepository()

    @request_response
    async def todos(request: Request) -> Response:
        if request.method == "GET":
            return JSONResponse([_to_json(todo) for todo in store.list()])
        if request.method == "POST":
            title = (await _read_body(request)).get("title")
            if not _valid_title(title):
                return _invalid_title()
            return JSONResponse(_to_json(store.create(title=title)), status_code=201)
        return _method_not_allowed()

    @request_response
    async def todo_detail(  # noqa: PLR0911 — one branch per field/error case
        request: Request,
    ) -> Response:
        todo_id = request.path_params["todo_id"]
        if request.method == "GET":
            try:
                return JSONResponse(_to_json(store.get(todo_id)))
            except KeyError:
                return _not_found()
        if request.method == "PATCH":
            body = await _read_body(request)
            title = body.get("title")
            done = body.get("done")
            if title is not None and not _valid_title(title):
                return _invalid_title()
            if done is not None and not isinstance(done, bool):
                return _invalid_done()
            try:
                return JSONResponse(
                    _to_json(store.update(todo_id, title=title, done=done))
                )
            except KeyError:
                return _not_found()
        if request.method == "DELETE":
            try:
                store.delete(todo_id)
            except KeyError:
                return _not_found()
            return Response(status_code=204)
        return _method_not_allowed()

    return Router(("/todos", todos), ("/todos/{todo_id:int}", todo_detail))


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))


if __name__ == "__main__":
    main()
