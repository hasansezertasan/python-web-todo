"""Todo JSON API with Flama and in-memory storage."""

import os
import typing as t

from flama import Flama, exceptions, http, types

from .models import Todo
from .repository import InMemoryTodoRepository
from .schemas import TodoCreate, TodoRead, TodoUpdate

TodoCreateBody = t.Annotated[types.Schema, types.SchemaMetadata(TodoCreate)]
TodoUpdateBody = t.Annotated[types.Schema, types.SchemaMetadata(TodoUpdate)]
TodoItem = t.Annotated[types.Schema, types.SchemaMetadata(TodoRead)]
TodoList = t.Annotated[types.SchemaList, types.SchemaMetadata(TodoRead)]


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _not_found() -> t.NoReturn:
    raise exceptions.HTTPException(status_code=404, detail="Todo not found")


def _validation_error_to_422(scope, receive, send, exc: exceptions.ValidationError) -> http.Response:
    # Flama reports schema-validation failures as 400 by default;
    # the shared JSON API contract expects 422, so remap them here.
    return http.JSONResponse({"detail": exc.detail}, status_code=422)


def create_app(repo: InMemoryTodoRepository | None = None) -> Flama:
    repo = repo or InMemoryTodoRepository()
    app = Flama(
        openapi={
            "info": {
                "title": "flama-api-memory",
                "version": "0.1.0",
                "description": "Todo JSON API built with Flama and in-memory storage.",
            },
        }
    )
    app.add_exception_handler(exceptions.ValidationError, _validation_error_to_422)

    @app.get("/todos")
    async def list_todos() -> TodoList:
        """List all todos."""
        return [_to_json(todo) for todo in repo.list()]

    @app.post("/todos")
    async def create_todo(data: TodoCreateBody) -> TodoItem:
        """Create a todo."""
        values = dict(data) if isinstance(data, dict) else data.model_dump()
        created = repo.create(title=values["title"])
        return http.JSONResponse(_to_json(created), status_code=201)

    @app.get("/todos/{todo_id:int}")
    async def get_todo(todo_id: int) -> TodoItem:
        """Get one todo."""
        try:
            return _to_json(repo.get(todo_id))
        except KeyError:
            _not_found()

    @app.patch("/todos/{todo_id:int}")
    async def update_todo(todo_id: int, data: TodoUpdateBody) -> TodoItem:
        """Update a todo."""
        values = dict(data) if isinstance(data, dict) else data.model_dump()
        try:
            updated = repo.update(todo_id, title=values.get("title"), done=values.get("done"))
        except KeyError:
            _not_found()
        return _to_json(updated)

    @app.delete("/todos/{todo_id:int}")
    async def delete_todo(todo_id: int) -> None:
        """Delete a todo."""
        try:
            repo.delete(todo_id)
        except KeyError:
            _not_found()
        return http.PlainTextResponse("", status_code=204)

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))


if __name__ == "__main__":
    main()
