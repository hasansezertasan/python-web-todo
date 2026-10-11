"""Todo JSON API with Litestar and SQLite storage via advanced-alchemy."""

from __future__ import annotations

import os
from pathlib import Path

from advanced_alchemy.extensions.litestar import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyInitPlugin,
)
from litestar import Litestar, Request, Response, delete, get, patch, post
from litestar.enums import MediaType
from litestar.exceptions import ValidationException
from litestar.openapi.config import OpenAPIConfig
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from msgspec import UNSET
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Todo
from .repository import todo_repository
from .schemas import TodoCreate, TodoRead, TodoUpdate

EXAMPLE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = EXAMPLE_DIR / "todos.db"
DEFAULT_DB_URL = f"sqlite+aiosqlite:///{DEFAULT_DB_PATH}"

DB_URL_ENV_VAR = "TODO_DB_URL"


def resolve_db_url(db_url: str | None = None) -> str:
    """Resolve the database URL: explicit arg, then env var, then the example-dir file."""
    return db_url or os.environ.get(DB_URL_ENV_VAR) or DEFAULT_DB_URL


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


@get("/todos", status_code=HTTP_200_OK)
async def list_todos(db_session: AsyncSession) -> list[TodoRead]:
    repo = todo_repository(db_session)
    return [_to_read(todo) for todo in await repo.list()]


@post("/todos", status_code=HTTP_201_CREATED)
async def create_todo(db_session: AsyncSession, data: TodoCreate) -> TodoRead:
    repo = todo_repository(db_session)
    todo = await repo.add(Todo(title=data.title, done=False))
    return _to_read(todo)


@get("/todos/{todo_id:int}", status_code=HTTP_200_OK)
async def get_todo(db_session: AsyncSession, todo_id: int) -> TodoRead:
    repo = todo_repository(db_session)
    return _to_read(await repo.get(todo_id))


@patch("/todos/{todo_id:int}", status_code=HTTP_200_OK)
async def update_todo(
    db_session: AsyncSession, todo_id: int, data: TodoUpdate
) -> TodoRead:
    repo = todo_repository(db_session)
    todo = await repo.get(todo_id)
    if data.title is not UNSET:
        todo.title = data.title
    if data.done is not UNSET:
        todo.done = data.done
    todo = await repo.update(todo)
    return _to_read(todo)


@delete("/todos/{todo_id:int}", status_code=HTTP_204_NO_CONTENT)
async def delete_todo(db_session: AsyncSession, todo_id: int) -> None:
    repo = todo_repository(db_session)
    await repo.get(todo_id)
    await repo.delete(todo_id)
    return None


def create_app(db_url: str | None = None) -> Litestar:
    """Create the Litestar app.

    Args:
        db_url: SQLAlchemy URL (e.g. ``sqlite+aiosqlite:////tmp/test.db``).
            Falls back to the ``TODO_DB_URL`` env var, then to
            ``todos.db`` inside this example directory. Tables are created
            at startup (``create_all=True``).
    """
    db_config = SQLAlchemyAsyncConfig(
        connection_string=resolve_db_url(db_url),
        create_all=True,
        session_config=AsyncSessionConfig(expire_on_commit=False),
    )
    return Litestar(
        route_handlers=[list_todos, create_todo, get_todo, update_todo, delete_todo],
        exception_handlers={ValidationException: _validation_error_to_422},
        plugins=[SQLAlchemyInitPlugin(config=db_config)],
        openapi_config=OpenAPIConfig(
            title="Todo API (Litestar, SQLite via advanced-alchemy)",
            version="0.1.0",
        ),
    )


app = create_app()
