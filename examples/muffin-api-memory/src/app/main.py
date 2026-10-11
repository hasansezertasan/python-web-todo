"""Todo JSON API with Muffin and in-memory storage."""

from muffin import Application, Response, ResponseJSON

from .models import Todo
from .repository import InMemoryTodoRepository


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


async def _body(request) -> dict:
    """Parsed JSON object, or {} when the body is missing/invalid.

    Muffin's ``request.json()`` raises ``ASGIDecodeError`` on an empty body,
    so catch it here and let the title check below answer 422 per contract.
    """
    try:
        data = await request.json()
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def create_app(repo: InMemoryTodoRepository | None = None) -> Application:
    repo = repo or InMemoryTodoRepository()
    app = Application()

    @app.route("/todos", methods=["GET"])
    async def list_todos(request):
        return [_to_json(todo) for todo in repo.list()]

    @app.route("/todos", methods=["POST"])
    async def create_todo(request):
        body = await _body(request)
        title = body.get("title")
        if not _valid_title(title):
            return ResponseJSON(
                {"error": "title must be a non-empty string"}, status_code=422
            )
        return 201, _to_json(repo.create(title=title))

    @app.route("/todos/{todo_id:int}", methods=["GET"])
    async def get_todo(request):
        todo_id = request.path_params["todo_id"]
        try:
            return _to_json(repo.get(todo_id))
        except KeyError:
            return ResponseJSON({"error": "Todo not found"}, status_code=404)

    @app.route("/todos/{todo_id:int}", methods=["PATCH"])
    async def update_todo(request):
        todo_id = request.path_params["todo_id"]
        body = await _body(request)
        title = body.get("title")
        done = body.get("done")
        if title is not None and not _valid_title(title):
            return ResponseJSON(
                {"error": "title must be a non-empty string"}, status_code=422
            )
        try:
            return _to_json(repo.update(todo_id, title=title, done=done))
        except KeyError:
            return ResponseJSON({"error": "Todo not found"}, status_code=404)

    @app.route("/todos/{todo_id:int}", methods=["DELETE"])
    async def delete_todo(request):
        todo_id = request.path_params["todo_id"]
        try:
            repo.delete(todo_id)
        except KeyError:
            return ResponseJSON({"error": "Todo not found"}, status_code=404)
        return Response(b"", status_code=204)

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
