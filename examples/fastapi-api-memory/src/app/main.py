"""Todo JSON API with FastAPI and in-memory storage."""

from fastapi import FastAPI, HTTPException, Response, status

from .models import Todo
from .repository import InMemoryTodoRepository
from .schemas import TodoCreate, TodoRead, TodoUpdate


def create_app(repo: InMemoryTodoRepository | None = None) -> FastAPI:
    repo = repo or InMemoryTodoRepository()
    app = FastAPI(title="Todo API (FastAPI, in-memory)")

    @app.get("/todos", response_model=list[TodoRead])
    def list_todos() -> list[Todo]:
        return repo.list()

    @app.post("/todos", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
    def create_todo(payload: TodoCreate) -> Todo:
        return repo.create(title=payload.title)

    @app.get("/todos/{todo_id}", response_model=TodoRead)
    def get_todo(todo_id: int) -> Todo:
        try:
            return repo.get(todo_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Todo not found") from None

    @app.patch("/todos/{todo_id}", response_model=TodoRead)
    def update_todo(todo_id: int, payload: TodoUpdate) -> Todo:
        try:
            return repo.update(todo_id, title=payload.title, done=payload.done)
        except KeyError:
            raise HTTPException(status_code=404, detail="Todo not found") from None

    @app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_todo(todo_id: int) -> Response:
        try:
            repo.delete(todo_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Todo not found") from None
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
