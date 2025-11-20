from toon.utils import override

from bpy.props import BoolProperty
from bpy.types import PropertyGroup

from .base import EntryBase, GroupBase
from .entry import Entry
from .naming import make_unique_name


class Group(GroupBase, Entry, PropertyGroup):
    show_expanded: BoolProperty(
        default=True,
        options={'LIBRARY_EDITABLE'}
    )

    def _key_to_index(self, key: int | str | EntryBase) -> int:
        if isinstance(key, int):
            if key < 0:
                return len(self.entries) + key
            else:
                return key
        elif isinstance(key, str):
            return self.entries.find(key)
        else:
            for i, entry in enumerate(self.entries):
                if entry == key:
                    return i

            return -1

    @override
    def first(self, key: int | str) -> EntryBase | None:
        index = self._key_to_index(key)

        if index < 0 or index >= len(self.entries):
            return None

        return self.entries[index]

    @override
    def find(self, key: str | EntryBase) -> int:
        return self._key_to_index(key)

    @override
    def add(self, name: str) -> EntryBase:
        name = make_unique_name(name, self.entries.keys())

        # Add entry.
        entry: EntryBase = self.entries.add()
        entry.on_add()
        entry.name = name

        return entry

    @override
    def remove(self, key: int | str | EntryBase):
        index = self._key_to_index(key)

        if index < 0 or index >= len(self.entries):
            return False

        # Remove entry.
        self.entries[index].on_remove()
        self.entries.remove(index)

        return True

    @override
    def clear(self) -> None:
        for i in range(len(self.entries)):
            self.remove(i)

    @override
    def move(self, src_key: int | str | EntryBase, dst_key: int | str | EntryBase):
        src_index = self._key_to_index(src_key)
        dst_index = self._key_to_index(dst_key)

        if src_index == dst_index:
            return False
        elif src_index < 0 or src_index >= len(self.entries):
            return False
        elif dst_index < 0 or dst_index >= len(self.entries):
            return False

        # Move entry.
        self.entries[src_index].on_move(self.entries[dst_index])
        self.entries.move(src_index, dst_index)

        return True

    @override
    def compare(self, other: EntryBase) -> int:
        other_entries = getattr(other, 'entries', [other])
        min_len = len(other_entries)
        result = 1

        if len(self.entries) == min_len:
            result = 0
        elif len(self.entries) < min_len:
            min_len = len(other_entries)
            result = -1

        for i in range(min_len):
            r = self.entries[i].compare(other_entries[i])

            if r != 0:
                return r

        return result

    @override
    def on_remove(self):
        for entry in reversed(self.entries):
            entry.on_remove()

    @override
    def on_move(self, dst: EntryBase):
        dst_entries = getattr(dst, 'entries', [dst])

        if self.entries and dst_entries:
            dst_entry = dst_entries[-1]
            src_entry_itr = self.entries

            if self.entries[0].compare(dst_entry) > 0:
                dst_entry = dst_entries[0]
                src_entry_itr = reversed(self.entries)

            for src_entry in src_entry_itr:
                src_entry.on_move(dst_entry)
                dst_entry = src_entry
