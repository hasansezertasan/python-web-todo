"""Process-local in-memory todo store, seeded empty."""

from .models import Todo


class InMemoryTodoRepository:
    def __init__(self) -> None:
        self._todos: dict[int, Todo] = {}
        self._next_id = 1

    def list(self) -> list[Todo]:
        return list(self._todos.values())

    def create(self, title: str) -> Todo:
        todo = Todo(id=self._next_id, title=title)
        self._todos[todo.id] = todo
        self._next_id += 1
        return todo

    def get(self, todo_id: int) -> Todo:
        return self._todos[todo_id]

    def update(
        self, todo_id: int, title: str | None = None, done: bool | None = None
    ) -> Todo:
        todo = self._todos[todo_id]
        if title is not None:
            todo.title = title
        if done is not None:
            todo.done = done
        return todo

    def delete(self, todo_id: int) -> None:
        del self._todos[todo_id]

    def reset(self) -> None:
        self._todos.clear()
        self._next_id = 1
