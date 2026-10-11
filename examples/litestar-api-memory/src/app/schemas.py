from typing import Annotated

import msgspec


class TodoCreate(msgspec.Struct):
    title: Annotated[str, msgspec.Meta(min_length=1)]


class TodoUpdate(msgspec.Struct):
    title: Annotated[str, msgspec.Meta(min_length=1)] | None = None
    done: bool | None = None


class TodoRead(msgspec.Struct):
    id: int
    title: str
    done: bool
