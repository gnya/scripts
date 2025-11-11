from bpy.props import CollectionProperty, IntProperty
from bpy.types import PropertyGroup

from .palette import PaletteEntry, PaletteGroup, Palette


class PalettePointer():
    def __init__(
            self, group: PaletteGroup, item: PaletteEntry | None,
            group_id: int = -1, item_id: int = -1
    ):
        self.group = group
        self.item = item
        self.group_id = group_id
        self.item_id = item_id


class PaletteSlot(PropertyGroup):
    item_id: IntProperty()

    group_id: IntProperty()


class PaletteUI(Palette, PropertyGroup):
    def _get_active_slot_id(self) -> int:
        if (
            self.active_slot_id_value < 0 or
            self.active_slot_id_value >= len(self.slots)
        ):
            return self.active_slot_id_value

        slot = self.slots[self.active_slot_id_value]

        if slot.item_id < 0:
            return self.active_slot_id_value

        if self.items[slot.group_id].show_expanded:
            return self.active_slot_id_value
        else:
            return self.active_slot_id_value - slot.item_id - 1

    def _set_active_slot_id(self, value: int):
        self.active_slot_id_value = value

    slots: CollectionProperty(type=PaletteSlot)

    active_slot_id_value: IntProperty(default=-1)

    active_slot_id: IntProperty(
        get=_get_active_slot_id, set=_set_active_slot_id
    )

    def get_item(self, key: PaletteSlot) -> PalettePointer | None:
        if key.group_id < 0 or key.group_id >= len(self.items):
            return None

        group = self.items[key.group_id]

        if key.item_id < 0 or key.item_id >= len(group.items):
            return PalettePointer(group, None, key.group_id, -1)

        item = group.items[key.item_id]

        return PalettePointer(group, item, key.group_id, key.item_id)

    def active_item(self) -> PalettePointer | None:
        slot_id = self.active_slot_id

        if slot_id < 0 or slot_id >= len(self.slots):
            return None

        return self.get_item(self.slots[slot_id])

    def update_slots(self):
        self.slots.clear()

        for group_id, group in enumerate(self.items):
            slot = self.slots.add()
            slot.item_id = -1
            slot.group_id = group_id

            for item_id in range(len(group.items)):
                slot = self.slots.add()
                slot.item_id = item_id
                slot.group_id = group_id
