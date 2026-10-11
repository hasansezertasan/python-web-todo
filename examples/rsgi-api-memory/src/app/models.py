"""Todo domain model."""

from dataclasses import dataclass


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "done": self.done}
