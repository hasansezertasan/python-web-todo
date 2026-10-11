"""Todo JSON API with Starlette and in-memory storage."""

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from .models import Todo
from .repository import InMemoryTodoRepository


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
    return JSONResponse({"detail": "Todo not found"}, status_code=404)


def _invalid_title() -> JSONResponse:
    return JSONResponse({"detail": "title must be a non-empty string"}, status_code=422)


def _invalid_done() -> JSONResponse:
    return JSONResponse({"detail": "done must be a boolean"}, status_code=422)


def create_app(repo: InMemoryTodoRepository | None = None) -> Starlette:
    repo = repo or InMemoryTodoRepository()

    async def list_todos(request: Request) -> JSONResponse:
        return JSONResponse([_to_json(todo) for todo in repo.list()])

    async def create_todo(request: Request) -> JSONResponse:
        body = await _read_body(request)
        title = body.get("title")
        if not _valid_title(title):
            return _invalid_title()
        return JSONResponse(_to_json(repo.create(title=title)), status_code=201)

    async def get_todo(request: Request) -> JSONResponse:
        try:
            return JSONResponse(_to_json(repo.get(request.path_params["todo_id"])))
        except KeyError:
            return _not_found()

    async def update_todo(request: Request) -> JSONResponse:
        body = await _read_body(request)
        title = body.get("title")
        done = body.get("done")
        if title is not None and not _valid_title(title):
            return _invalid_title()
        if done is not None and not isinstance(done, bool):
            return _invalid_done()
        try:
            return JSONResponse(
                _to_json(
                    repo.update(request.path_params["todo_id"], title=title, done=done)
                )
            )
        except KeyError:
            return _not_found()

    async def delete_todo(request: Request) -> Response:
        try:
            repo.delete(request.path_params["todo_id"])
        except KeyError:
            return _not_found()
        return Response(status_code=204)

    return Starlette(
        routes=[
            Route("/todos", endpoint=list_todos, methods=["GET"]),
            Route("/todos", endpoint=create_todo, methods=["POST"]),
            Route("/todos/{todo_id:int}", endpoint=get_todo, methods=["GET"]),
            Route("/todos/{todo_id:int}", endpoint=update_todo, methods=["PATCH"]),
            Route("/todos/{todo_id:int}", endpoint=delete_todo, methods=["DELETE"]),
        ]
    )


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
