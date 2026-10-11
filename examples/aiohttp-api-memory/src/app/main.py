"""Todo JSON API with aiohttp and in-memory storage."""

from aiohttp import web

from .models import todo_to_dict
from .repository import InMemoryTodoRepository


def _not_found() -> web.Response:
    return web.json_response({"detail": "Todo not found"}, status=404)


def _invalid_title() -> web.Response:
    return web.json_response(
        {"detail": "Title must be a non-empty string"}, status=422
    )


def _parse_id(raw: str) -> int | None:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def create_app(repo: InMemoryTodoRepository | None = None) -> web.Application:
    repo = repo or InMemoryTodoRepository()
    app = web.Application()

    async def list_todos(request: web.Request) -> web.Response:
        return web.json_response([todo_to_dict(t) for t in repo.list()])

    async def create_todo(request: web.Request) -> web.Response:
        try:
            payload = await request.json()
        except Exception:
            return _invalid_title()
        title = payload.get("title") if isinstance(payload, dict) else None
        if not isinstance(title, str) or not title.strip():
            return _invalid_title()
        todo = repo.create(title=title)
        return web.json_response(todo_to_dict(todo), status=201)

    async def get_todo(request: web.Request) -> web.Response:
        todo_id = _parse_id(request.match_info["todo_id"])
        if todo_id is None:
            return _not_found()
        try:
            todo = repo.get(todo_id)
        except KeyError:
            return _not_found()
        return web.json_response(todo_to_dict(todo))

    async def update_todo(request: web.Request) -> web.Response:
        todo_id = _parse_id(request.match_info["todo_id"])
        if todo_id is None:
            return _not_found()
        try:
            payload = await request.json()
        except Exception:
            return _invalid_title()
        if not isinstance(payload, dict):
            return _invalid_title()
        title = payload.get("title", None)
        done = payload.get("done", None)
        if "title" in payload and (
            not isinstance(title, str) or not title.strip()
        ):
            return _invalid_title()
        if "done" in payload and not isinstance(done, bool):
            return web.json_response(
                {"detail": "Done must be a boolean"}, status=422
            )
        try:
            todo = repo.update(todo_id, title=title, done=done)
        except KeyError:
            return _not_found()
        return web.json_response(todo_to_dict(todo))

    async def delete_todo(request: web.Request) -> web.Response:
        todo_id = _parse_id(request.match_info["todo_id"])
        if todo_id is None:
            return _not_found()
        try:
            repo.delete(todo_id)
        except KeyError:
            return _not_found()
        return web.Response(status=204)

    app.router.add_get("/todos", list_todos)
    app.router.add_post("/todos", create_todo)
    app.router.add_get("/todos/{todo_id}", get_todo)
    app.router.add_patch("/todos/{todo_id}", update_todo)
    app.router.add_delete("/todos/{todo_id}", delete_todo)
    return app


app = create_app()


def main() -> None:
    web.run_app(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
