"""SQLAlchemy model for the todo API (advanced-alchemy base)."""

from sqlalchemy.orm import Mapped, mapped_column

from advanced_alchemy.base import BigIntBase


class Todo(BigIntBase):
    """Todo item with an integer primary key (``id`` from ``BigIntBase``)."""

    __tablename__ = "todos"

    title: Mapped[str]
    done: Mapped[bool] = mapped_column(default=False)
