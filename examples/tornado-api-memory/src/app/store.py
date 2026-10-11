"""In-memory todo store. Process-local; starts empty."""

from dataclasses import dataclass


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False


class TodoStore:
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

    def get(self, todo_id: int) -> Todo | None:
        return self._todos.get(todo_id)

    def update(
        self, todo_id: int, title: str | None = None, done: bool | None = None
    ) -> Todo | None:
        todo = self._todos.get(todo_id)
        if todo is None:
            return None
        if title is not None:
            todo.title = title
        if done is not None:
            todo.done = done
        return todo

    def delete(self, todo_id: int) -> bool:
        if todo_id not in self._todos:
            return False
        del self._todos[todo_id]
        return True


def todo_to_dict(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}
