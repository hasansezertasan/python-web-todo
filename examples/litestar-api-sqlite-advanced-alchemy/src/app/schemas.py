"""Request/response schemas (msgspec Structs, Litestar-native)."""

from typing import Union

from msgspec import UNSET, Meta, Struct, UnsetType
from typing_extensions import Annotated


class TodoCreate(Struct):
    title: Annotated[str, Meta(min_length=1)]


class TodoUpdate(Struct):
    title: Union[Annotated[str, Meta(min_length=1)], UnsetType] = UNSET
    done: Union[bool, UnsetType] = UNSET


class TodoRead(Struct):
    id: int
    title: str
    done: bool
