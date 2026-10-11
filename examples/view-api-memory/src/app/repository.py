import threading

from .models import Todo


class InMemoryTodoRepository:
    """Process-local store. Starts empty; data loss on restart is acceptable."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._todos: dict[int, Todo] = {}
        self._next_id = 1

    def list(self) -> list[Todo]:
        with self._lock:
            return list(self._todos.values())

    def create(self, title: str) -> Todo:
        with self._lock:
            todo = Todo(id=self._next_id, title=title)
            self._todos[todo.id] = todo
            self._next_id += 1
            return todo

    def get(self, todo_id: int) -> Todo:
        with self._lock:
            return self._todos[todo_id]

    def update(
        self, todo_id: int, title: str | None = None, done: bool | None = None
    ) -> Todo:
        with self._lock:
            todo = self._todos[todo_id]
            if title is not None:
                todo.title = title
            if done is not None:
                todo.done = done
            return todo

    def delete(self, todo_id: int) -> None:
        with self._lock:
            del self._todos[todo_id]
