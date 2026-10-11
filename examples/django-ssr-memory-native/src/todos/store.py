"""Process-local in-memory store. Starts empty; data loss on restart is fine."""

import threading
from dataclasses import dataclass


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False


class TodoStore:
    """Thread-safe store used by the views. Tests reset it via ``clear()``."""

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

    def toggle(self, todo_id: int) -> Todo:
        with self._lock:
            todo = self._todos[todo_id]
            todo.done = not todo.done
            return todo

    def delete(self, todo_id: int) -> None:
        with self._lock:
            del self._todos[todo_id]

    def clear(self) -> None:
        """Reset to the initial empty state (used by tests for fresh state)."""
        with self._lock:
            self._todos.clear()
            self._next_id = 1


store = TodoStore()


def reset_store() -> TodoStore:
    """Clear the shared store and return it (fresh-state hook for tests)."""
    store.clear()
    return store
