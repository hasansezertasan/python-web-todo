from dataclasses import asdict, dataclass


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False


def todo_to_dict(todo: Todo) -> dict:
    return asdict(todo)
