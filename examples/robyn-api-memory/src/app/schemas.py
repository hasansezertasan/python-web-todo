from pydantic import BaseModel


class TodoRead(BaseModel):
    id: int
    title: str
    done: bool
