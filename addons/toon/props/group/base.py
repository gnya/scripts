from __future__ import annotations
from typing import MutableSequence


class EntryBase():
    name: str

    def parent(self) -> GroupBase | tuple[list[str], list[EntryBase]] | None:
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


class GroupBase(EntryBase):
    entries: MutableSequence[EntryBase]

    show_expanded: bool

    def get_entry(self, key: int | str | EntryBase) -> EntryBase | None:
        raise NotImplementedError()

    def find(self, key: str | EntryBase) -> int:
        raise NotImplementedError()

    def add(self, name: str) -> EntryBase:
        raise NotImplementedError()

    def remove(self, key: int | str | EntryBase) -> bool:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def move(self, src_key: int | str | EntryBase, dst_key: int | str | EntryBase) -> bool:
        raise NotImplementedError()
