from pydantic import BaseModel


class TodoRead(BaseModel):
    """Response shape for a todo item. Used as the return annotation on
    endpoints so Responder validates responses and includes the item schema
    (id/title/done) in the generated OpenAPI document."""

    id: int
    title: str
    done: bool
