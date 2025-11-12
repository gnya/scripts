from bpy.props import BoolProperty
from bpy.types import PropertyGroup

from toon.utils import override

from .base import EntryBase, GroupBase
from .entry import Entry
from .naming import make_unique_name


class Group(GroupBase, Entry, PropertyGroup):
    show_expanded: BoolProperty()

    def _key_to_index(self, key: int | str | EntryBase) -> int:
        if isinstance(key, int):
            if key < 0:
                return len(self.items) + key
            else:
                return key
        elif isinstance(key, str):
            return self.items.find(key)
        else:
            return self.items.find(key.name)

    @override
    def add(self, name: str) -> EntryBase:
        name = make_unique_name(name, self.items.keys())

        # Add item.
        item: EntryBase = self.items.add()
        item.on_add()
        item.name = name

        return item

    @override
    def remove(self, key: int | str | EntryBase):
        index = self._key_to_index(key)

        if index < 0 or index >= len(self.items):
            return False

        # Remove item.
        self.items[index].on_remove()
        self.items.remove(index)

        return True

    @override
    def move(self, src_key: int | str | EntryBase, dst_key: int | str | EntryBase):
        src_index = self._key_to_index(src_key)
        dst_index = self._key_to_index(dst_key)

        if src_index == dst_index:
            return False
        elif src_index < 0 or src_index >= len(self.items):
            return False
        elif dst_index < 0 or dst_index >= len(self.items):
            return False

        # Move item.
        self.items[src_index].on_move(self.items[dst_index])
        self.items.move(src_index, dst_index)

        return True

    @override
    def compare(self, other: EntryBase) -> int:
        other_items = getattr(other, 'items', [other])
        min_len = len(other_items)
        result = 1

        if len(self.items) == min_len:
            result = 0
        elif len(self.items) < min_len:
            min_len = len(other_items)
            result = -1

        for i in range(min_len):
            r = self.items[i].compare(other_items[i])

            if r != 0:
                return r

        return result

    @override
    def on_remove(self):
        for item in reversed(self.items):
            item.on_remove()

    @override
    def on_move(self, dst: EntryBase):
        dst_items = getattr(dst, 'items', [dst])

        if self.items and dst_items:
            dst_item = dst_items[-1]
            src_item_itr = self.items

            if self.items[0].compare(dst_item) > 0:
                dst_item = dst_items[0]
                src_item_itr = reversed(self.items)

            for src_item in src_item_itr:
                src_item.on_move(dst_item)
                dst_item = src_item
