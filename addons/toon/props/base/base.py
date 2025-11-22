from __future__ import annotations
from typing import MutableSequence, Generic, TypeVar

E = TypeVar('E', bound='EntryBase')


class EntryBase():
    name: str

    def parent(self) -> GroupBase[EntryBase] | tuple[list[str], list[EntryBase]] | None:
        raise NotImplementedError()

    def compare(self, other: EntryBase) -> int:
        raise NotImplementedError()

    def on_rename(self):
        pass

    def on_add(self):
        pass

    def on_remove(self):
        pass

    def on_move(self, dst: EntryBase):
        pass


class GroupBase(Generic[E]):
    entries: MutableSequence[E]

    show_expanded: bool

    def first(self, key: int | str) -> E | None:
        raise NotImplementedError()

    def find(self, key: str | E) -> int:
        raise NotImplementedError()

    def add(self, name: str) -> E:
        raise NotImplementedError()

    def remove(self, key: int | str | E) -> bool:
        raise NotImplementedError()

    def clear(self) -> bool:
        raise NotImplementedError()

    def move(self, src_key: int | str | E, dst_key: int | str | E) -> bool:
        raise NotImplementedError()
