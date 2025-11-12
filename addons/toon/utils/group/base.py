from typing import Any, MutableSequence


class EntryBase():
    name: str

    def parent(self) -> Any | None:
        raise NotImplementedError()

    def compare(self, other: 'EntryBase') -> int:
        raise NotImplementedError()

    def on_rename(self):
        pass

    def on_add(self):
        pass

    def on_remove(self):
        pass

    def on_move(self, dst: 'EntryBase'):
        pass


class GroupBase(EntryBase):
    entries: MutableSequence[EntryBase]

    show_expanded: bool

    def add(self, name: str) -> EntryBase:
        raise NotImplementedError()

    def remove(self, key: int | str | EntryBase) -> bool:
        raise NotImplementedError()

    def move(self, src_key: int | str | EntryBase, dst_key: int | str | EntryBase) -> bool:
        raise NotImplementedError()
