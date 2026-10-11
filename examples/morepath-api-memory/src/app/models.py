from dataclasses import dataclass


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False


class TodoCollection:
    """Model for the `/todos` collection path."""

    def __init__(self, repo: object) -> None:
        self.repo = repo
