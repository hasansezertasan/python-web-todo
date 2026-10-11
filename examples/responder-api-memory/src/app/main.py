"""Todo JSON API with Responder and in-memory storage."""

import responder

from .models import Todo
from .repository import InMemoryTodoRepository
from .schemas import TodoRead


def _todo_to_dict(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _not_found(resp: responder.Response) -> None:
    resp.status_code = 404
    resp.media = {"detail": "Todo not found"}


def _invalid(resp: responder.Response, detail: str) -> None:
    resp.status_code = 422
    resp.media = {"detail": detail}


def create_app(  # noqa: PLR0915 — one factory wiring all five routes
    repo: InMemoryTodoRepository | None = None,
) -> responder.API:
    repo = repo or InMemoryTodoRepository()
    api = responder.API(
        title="Todo API (Responder, in-memory)", version="0.1.0", openapi="3.0.2"
    )

    @api.route("/todos", methods=["GET"])
    def list_todos(req: responder.Request, resp: responder.Response) -> list[TodoRead]:
        resp.media = [_todo_to_dict(todo) for todo in repo.list()]

    @api.route("/todos", methods=["POST"], status_code=201)
    def create_todo(req: responder.Request, resp: responder.Response) -> TodoRead:
        try:
            payload = req.media_sync()
        except Exception:
            payload = None
        title = payload.get("title") if isinstance(payload, dict) else None
        if not isinstance(title, str) or title == "":
            _invalid(resp, "Title must be a non-empty string")
            return None
        todo = repo.create(title=title)
        resp.status_code = 201
        resp.media = _todo_to_dict(todo)
        return None

    @api.route("/todos/{todo_id}", methods=["GET"])
    def get_todo(
        req: responder.Request, resp: responder.Response, *, todo_id: str
    ) -> TodoRead:
        try:
            target = int(todo_id)
        except (TypeError, ValueError):
            _not_found(resp)
            return None
        try:
            todo = repo.get(target)
        except KeyError:
            _not_found(resp)
            return None
        resp.media = _todo_to_dict(todo)
        return None

    @api.route("/todos/{todo_id}", methods=["PATCH"])
    def update_todo(
        req: responder.Request, resp: responder.Response, *, todo_id: str
    ) -> TodoRead:
        try:
            target = int(todo_id)
        except (TypeError, ValueError):
            _not_found(resp)
            return None
        try:
            payload = req.media_sync()
        except Exception:
            payload = None
        if not isinstance(payload, dict):
            _invalid(resp, "Request body must be a JSON object")
            return None
        title = payload.get("title")
        done = payload.get("done")
        if "title" in payload and (not isinstance(title, str) or title == ""):
            _invalid(resp, "Title must be a non-empty string")
            return None
        if "done" in payload and not isinstance(done, bool):
            _invalid(resp, "Done must be a boolean")
            return None
        try:
            todo = repo.update(
                target,
                title=title if "title" in payload else None,
                done=done if "done" in payload else None,
            )
        except KeyError:
            _not_found(resp)
            return None
        resp.media = _todo_to_dict(todo)
        return None

    @api.route("/todos/{todo_id}", methods=["DELETE"], status_code=204)
    def delete_todo(
        req: responder.Request, resp: responder.Response, *, todo_id: str
    ) -> None:
        try:
            target = int(todo_id)
        except (TypeError, ValueError):
            _not_found(resp)
            return
        try:
            repo.delete(target)
        except KeyError:
            _not_found(resp)
            return
        resp.status_code = 204
        resp.media = None

    return api


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
