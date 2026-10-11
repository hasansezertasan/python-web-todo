"""Todo JSON API with Litestar and in-memory storage."""

from litestar import Litestar, Request, Response, delete, get, patch, post
from litestar.enums import MediaType
from litestar.exceptions import NotFoundException, ValidationException
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from .models import Todo
from .repository import InMemoryTodoRepository
from .schemas import TodoCreate, TodoRead, TodoUpdate


def _to_read(todo: Todo) -> TodoRead:
    return TodoRead(id=todo.id, title=todo.title, done=todo.done)


def _validation_error_to_422(request: Request, exc: ValidationException) -> Response:
    # Litestar reports request-validation failures as 400 by default;
    # the shared JSON API contract expects 422, so remap them here.
    return Response(
        content={
            "status_code": HTTP_422_UNPROCESSABLE_ENTITY,
            "detail": exc.detail,
            "extra": exc.extra or {},
        },
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        media_type=MediaType.JSON,
    )


def create_app(repo: InMemoryTodoRepository | None = None) -> Litestar:
    repo = repo or InMemoryTodoRepository()

    @get("/todos", status_code=HTTP_200_OK)
    async def list_todos() -> list[TodoRead]:
        return [_to_read(todo) for todo in repo.list()]

    @post("/todos", status_code=HTTP_201_CREATED)
    async def create_todo(data: TodoCreate) -> TodoRead:
        return _to_read(repo.create(title=data.title))

    @get("/todos/{todo_id:int}", status_code=HTTP_200_OK)
    async def get_todo(todo_id: int) -> TodoRead:
        try:
            return _to_read(repo.get(todo_id))
        except KeyError:
            raise NotFoundException(detail="Todo not found") from None

    @patch("/todos/{todo_id:int}", status_code=HTTP_200_OK)
    async def update_todo(todo_id: int, data: TodoUpdate) -> TodoRead:
        try:
            return _to_read(repo.update(todo_id, title=data.title, done=data.done))
        except KeyError:
            raise NotFoundException(detail="Todo not found") from None

    @delete("/todos/{todo_id:int}", status_code=HTTP_204_NO_CONTENT)
    async def delete_todo(todo_id: int) -> None:
        try:
            repo.delete(todo_id)
        except KeyError:
            raise NotFoundException(detail="Todo not found") from None
        return None

    return Litestar(
        route_handlers=[list_todos, create_todo, get_todo, update_todo, delete_todo],
        exception_handlers={ValidationException: _validation_error_to_422},
    )


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
