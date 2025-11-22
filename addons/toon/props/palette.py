from bpy.props import BoolProperty, CollectionProperty, IntProperty
from bpy.types import PropertyGroup

from .group import Group
from .palette_entry import PaletteEntry


class PaletteGroup(Group[PaletteEntry], PropertyGroup):
    pass


class PalettePointer():
    def __init__(
            self, group: PaletteGroup, entry: PaletteEntry | None,
            group_id: int = -1, entry_id: int = -1
    ):
        self.group = group
        self.entry = entry
        self.group_id = group_id
        self.entry_id = entry_id


class PaletteSlot(PropertyGroup):
    entry_id: IntProperty()

    group_id: IntProperty()


class Palette(Group[PaletteGroup], PropertyGroup):
    def _get_active_slot_id(self) -> int:
        if (
            self.active_slot_id_value < 0 or
            self.active_slot_id_value >= len(self.slots)
        ):
            return self.active_slot_id_value

        slot = self.slots[self.active_slot_id_value]

        if self.entries[slot.group_id].show_expanded:
            return self.active_slot_id_value
        else:
            return self.active_slot_id_value - slot.entry_id - 1

    def _set_active_slot_id(self, value: int):
        self.active_slot_id_value = value

    is_available: BoolProperty(default=False)

    order: IntProperty(
        default=-1,
        options={'LIBRARY_EDITABLE'}
    )

    slots: CollectionProperty(
        type=PaletteSlot,
        options={'LIBRARY_EDITABLE'}
    )

    active_slot_id_value: IntProperty(
        default=-1,
        options={'LIBRARY_EDITABLE'}
    )

    active_slot_id: IntProperty(
        options={'LIBRARY_EDITABLE'},
        get=_get_active_slot_id, set=_set_active_slot_id
    )

    def get_pointer(self, key: PaletteSlot) -> PalettePointer | None:
        if key.group_id < 0 or key.group_id >= len(self.entries):
            return None

        group = self.entries[key.group_id]

        if key.entry_id < 0 or key.entry_id >= len(group.entries):
            return PalettePointer(group, None, key.group_id, -1)

        entry = group.entries[key.entry_id]

        return PalettePointer(group, entry, key.group_id, key.entry_id)

    def active_pointer(self) -> PalettePointer | None:
        slot_id = self.active_slot_id

        if slot_id < 0 or slot_id >= len(self.slots):
            return None

        return self.get_pointer(self.slots[slot_id])

    def update_slots(self):
        self.slots.clear()

        for group_id, group in enumerate(self.entries):
            slot = self.slots.add()
            slot.entry_id = -1
            slot.group_id = group_id

            for entry_id in range(len(group.entries)):
                slot = self.slots.add()
                slot.entry_id = entry_id
                slot.group_id = group_id
