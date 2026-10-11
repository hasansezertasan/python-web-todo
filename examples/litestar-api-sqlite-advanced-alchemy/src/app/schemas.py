"""Request/response schemas (msgspec Structs, Litestar-native)."""

from typing import Annotated

from msgspec import UNSET, Meta, Struct, UnsetType


class TodoCreate(Struct):
    title: Annotated[str, Meta(min_length=1)]


class TodoUpdate(Struct):
    title: Annotated[str, Meta(min_length=1)] | UnsetType = UNSET
    done: bool | UnsetType = UNSET


class TodoRead(Struct):
    id: int
    title: str
    done: bool
