from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    title: str = Field(min_length=1)


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    done: bool | None = None


class TodoRead(BaseModel):
    id: int
    title: str
    done: bool
