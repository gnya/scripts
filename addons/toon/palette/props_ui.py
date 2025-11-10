from bpy.types import PropertyGroup
from bpy.props import CollectionProperty, IntProperty

from .props_palette import PaletteItem, PaletteGroup, Palette


class PalettePointer():
    def __init__(
            self, item: PaletteItem | None, group: PaletteGroup | None,
            item_id: int = -1, group_id: int = -1
    ):
        self.item = item
        self.group = group
        self.item_id = item_id
        self.group_id = group_id

    # When a pointer is null, it evaluates to False in an if statement.
    def __bool__(self):
        return not (
            self.item is None and self.group is None and
            self.item_id < 0 and self.group_id < 0
        )


class PaletteUIItem(PropertyGroup):
    item_id: IntProperty()

    group_id: IntProperty()


class PaletteUI(Palette, PropertyGroup):
    def get_active_ui_index(self):
        if (
            self.actual_active_ui_index < 0 or
            self.actual_active_ui_index >= len(self.ui_items)
        ):
            return self.actual_active_ui_index

        ui_item = self.ui_items[self.actual_active_ui_index]

        if ui_item.item_id < 0:
            return self.actual_active_ui_index

        if self.items[ui_item.group_id].show_expanded:
            return self.actual_active_ui_index
        else:
            return self.actual_active_ui_index - ui_item.item_id - 1

    def set_active_ui_index(self, value):
        self.actual_active_ui_index = value

    ui_items: CollectionProperty(type=PaletteUIItem)

    actual_active_ui_index: IntProperty(default=-1)

    active_ui_index: IntProperty(
        get=get_active_ui_index, set=set_active_ui_index
    )

    def get_item(self, key: PaletteUIItem) -> PalettePointer:
        if key.group_id < 0 or key.group_id >= len(self.items):
            return PalettePointer(None, None, -1, -1)

        group: PaletteGroup = self.items[key.group_id]

        if key.item_id < 0 or key.item_id >= len(group.items):
            return PalettePointer(None, group, -1, key.group_id)

        item: PaletteItem = group.items[key.item_id]

        return PalettePointer(item, group, key.item_id, key.group_id)

    def active_item(self) -> PalettePointer:
        ui_index = self.active_ui_index

        if ui_index < 0 or ui_index >= len(self.ui_items):
            return PalettePointer(None, None, -1, -1)

        return self.get_item(self.ui_items[ui_index])

    def update(self):
        self.ui_items.clear()

        for group_id, group in enumerate(self.items):
            ui_item = self.ui_items.add()
            ui_item.item_id = -1
            ui_item.group_id = group_id

            for item_id in range(len(group.items)):
                ui_item = self.ui_items.add()
                ui_item.item_id = item_id
                ui_item.group_id = group_id
