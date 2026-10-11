"""advanced-alchemy repository for todos."""

from sqlalchemy.ext.asyncio import AsyncSession

from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from .models import Todo


class TodoRepository(SQLAlchemyAsyncRepository[Todo]):
    """SQLAlchemy async repository for :class:`Todo`."""

    model_type = Todo


def todo_repository(db_session: AsyncSession) -> TodoRepository:
    """Build a request-scoped repository with auto-commit enabled."""
    return TodoRepository(session=db_session, auto_commit=True)
