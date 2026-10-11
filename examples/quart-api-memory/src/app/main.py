"""Todo JSON API with Quart and in-memory storage."""

from quart import Quart, jsonify, request

from .models import Todo
from .repository import InMemoryTodoRepository


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


def create_app(repo: InMemoryTodoRepository | None = None) -> Quart:
    repo = repo or InMemoryTodoRepository()
    app = Quart(__name__)

    @app.get("/todos")
    async def list_todos():
        return jsonify([_to_json(todo) for todo in await repo.list()])

    @app.post("/todos")
    async def create_todo():
        body = await request.get_json(silent=True) or {}
        title = body.get("title")
        if not _valid_title(title):
            return jsonify({"error": "title must be a non-empty string"}), 422
        return jsonify(_to_json(await repo.create(title=title))), 201

    @app.get("/todos/<int:todo_id>")
    async def get_todo(todo_id: int):
        try:
            return jsonify(_to_json(await repo.get(todo_id)))
        except KeyError:
            return jsonify({"error": "Todo not found"}), 404

    @app.patch("/todos/<int:todo_id>")
    async def update_todo(todo_id: int):
        body = await request.get_json(silent=True) or {}
        title = body.get("title")
        done = body.get("done")
        if title is not None and not _valid_title(title):
            return jsonify({"error": "title must be a non-empty string"}), 422
        try:
            return jsonify(
                _to_json(await repo.update(todo_id, title=title, done=done))
            )
        except KeyError:
            return jsonify({"error": "Todo not found"}), 404

    @app.delete("/todos/<int:todo_id>")
    async def delete_todo(todo_id: int):
        try:
            await repo.delete(todo_id)
        except KeyError:
            return jsonify({"error": "Todo not found"}), 404
        return "", 204

    return app


app = create_app()


def main() -> None:
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
