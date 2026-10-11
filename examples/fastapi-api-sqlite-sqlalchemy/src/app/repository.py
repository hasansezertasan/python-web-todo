from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Todo


class SqlAlchemyTodoRepository:
    """SQLite-backed store. Raises KeyError for unknown ids (mapped to 404)."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def list(self) -> list[Todo]:
        return list(self._db.scalars(select(Todo).order_by(Todo.id)).all())

    def create(self, title: str) -> Todo:
        todo = Todo(title=title, done=False)
        self._db.add(todo)
        self._db.commit()
        self._db.refresh(todo)
        return todo

    def get(self, todo_id: int) -> Todo:
        todo = self._db.get(Todo, todo_id)
        if todo is None:
            raise KeyError(todo_id)
        return todo

    def update(
        self, todo_id: int, title: str | None = None, done: bool | None = None
    ) -> Todo:
        todo = self.get(todo_id)
        if title is not None:
            todo.title = title
        if done is not None:
            todo.done = done
        self._db.commit()
        self._db.refresh(todo)
        return todo

    def delete(self, todo_id: int) -> None:
        todo = self.get(todo_id)
        self._db.delete(todo)
        self._db.commit()
