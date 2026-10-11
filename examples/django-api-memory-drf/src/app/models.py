"""Plain dataclass Todo. No ORM models are used in this example."""

from dataclasses import dataclass


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False
