"""Todo JSON API with socketify.py and in-memory storage."""

import json
import os

from socketify import App

from .models import Todo
from .repository import InMemoryTodoRepository


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _send_json(res, status: int, payload: dict | list) -> None:
    res.write_status(status)
    res.write_header("Content-Type", "application/json")
    res.end(json.dumps(payload))


def _error(res, status: int, message: str) -> None:
    _send_json(res, status, {"error": message})


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


async def _body(res, req) -> dict:
    try:
        data = await res.get_json()
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _parse_id(res, req) -> int | None:
    try:
        return int(req.get_parameter(0))
    except (TypeError, ValueError):
        _error(res, 404, "Todo not found")
        return None


def create_app(repo: InMemoryTodoRepository | None = None) -> App:
    repo = repo or InMemoryTodoRepository()
    app = App()

    app.get("/todos", lambda res, req: _send_json(res, 200, [_to_json(t) for t in repo.list()]))

    async def create_todo(res, req):
        title = (await _body(res, req)).get("title")
        if not _valid_title(title):
            _error(res, 422, "title must be a non-empty string")
            return
        _send_json(res, 201, _to_json(repo.create(title=title)))

    app.post("/todos", create_todo)

    def get_todo(res, req):
        todo_id = _parse_id(res, req)
        if todo_id is None:
            return
        try:
            _send_json(res, 200, _to_json(repo.get(todo_id)))
        except KeyError:
            _error(res, 404, "Todo not found")

    app.get("/todos/:id", get_todo)

    async def update_todo(res, req):
        todo_id = _parse_id(res, req)
        if todo_id is None:
            return
        body = await _body(res, req)
        title = body.get("title")
        done = body.get("done")
        if title is not None and not _valid_title(title):
            _error(res, 422, "title must be a non-empty string")
            return
        if done is not None and not isinstance(done, bool):
            _error(res, 422, "done must be a boolean")
            return
        try:
            _send_json(res, 200, _to_json(repo.update(todo_id, title=title, done=done)))
        except KeyError:
            _error(res, 404, "Todo not found")

    app.patch("/todos/:id", update_todo)

    def delete_todo(res, req):
        todo_id = _parse_id(res, req)
        if todo_id is None:
            return
        try:
            repo.delete(todo_id)
        except KeyError:
            _error(res, 404, "Todo not found")
            return
        res.write_status(204)
        res.end_without_body()

    app.delete("/todos/:id", delete_todo)

    return app


app = create_app()


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    app.listen(port, lambda config: print(f"Listening on port {config.port} now"))
    app.run()


if __name__ == "__main__":
    main()
