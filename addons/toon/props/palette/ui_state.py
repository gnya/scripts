from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

import bpy
from bpy.app.handlers import persistent, redo_post, undo_post
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import NodeTree, PropertyGroup, WindowManager

from toon.palette import (
    get_facade,
    get_groups,
    get_library,
    get_palette,
    get_palette_name,
    set_palette_name,
)
from toon.utils import node_group_import_post

from .node import ToonPaletteSearchIndex
from .ui_item import ToonPaletteUIItem
from .view import (
    get_active_index,
    get_show_expanded,
    set_active_index,
    set_show_expanded,
)

if TYPE_CHECKING:
    from bpy.types import Scene

    from toon.palette import ToonPalette, ToonPaletteGroup


class ToonPaletteUIPaletteState(PropertyGroup):
    header: PointerProperty(type=NodeTree)

    list_items: CollectionProperty(type=ToonPaletteUIItem)

    palette_index: IntProperty(default=-1)

    def _get_palette_name(self) -> str:
        return get_palette_name(self.header)

    def _set_palette_name(self, value: str):
        set_palette_name(self.header, value)
        ToonPaletteSearchIndex.request_update()

    palette_name: StringProperty(get=_get_palette_name, set=_set_palette_name)

    def _get_active_index(self) -> int:
        index = get_active_index(self.header)
        index = min(index, len(self.list_items) - 1)

        if index < 0:
            return -1
        elif not (item := self.list_items[index]).show_expanded:
            return item.header_index
        else:
            return index

    def _set_active_index(self, value: int):
        set_active_index(self.header, value)

    active_index: IntProperty(get=_get_active_index, set=_set_active_index)

    def _get_show_expanded(self) -> bool:
        return get_show_expanded(self.header)

    def _set_show_expanded(self, value: bool):
        set_show_expanded(self.header, value)

    show_expanded: BoolProperty(get=_get_show_expanded, set=_set_show_expanded)

    def active_item(self) -> ToonPaletteUIItem | None:
        if (index := self.active_index) < 0:
            return None
        else:
            return self.list_items[index]

    def is_orphans(self) -> bool:
        return self.header is None

    def is_linked(self) -> bool:
        return get_library(self.header) != ""

    def palette_data(self) -> ToonPalette | None:
        return get_palette(self.header)

    def groups_data(self) -> Iterator[ToonPaletteGroup]:
        return get_groups(self.header)

    def active_group_data(self) -> ToonPaletteGroup | None:
        if (item := self.active_item()) is None:
            return None
        else:
            return item.group_data()

    def init(self, palette: ToonPalette, palette_index: int):
        self.header = palette.header
        self.palette_index = palette_index
        header_index = 0

        for group_index, group in enumerate(palette.groups()):
            item = self.list_items.add()
            item.init(group, group_index, header_index)
            colors = list(group.colors())

            for color in colors:
                item = self.list_items.add()
                item.init(group, group_index, header_index, color)

            header_index += len(colors) + 1


class ToonPaletteUIState(PropertyGroup):
    PROP_NAME = "toon_palette_ui_state"

    list_states: CollectionProperty(type=ToonPaletteUIPaletteState)

    update_requested: BoolProperty(default=True)

    def update(self):
        if not self.update_requested:
            return

        self.list_states.clear()

        for index, palette in enumerate(get_facade().palettes()):
            state = self.list_states.add()
            state.init(palette, index)

        self.update_requested = False

    @staticmethod
    def instance() -> ToonPaletteUIState:
        id = bpy.context.window_manager

        return getattr(id, ToonPaletteUIState.PROP_NAME)

    @staticmethod
    def request_update():
        states = ToonPaletteUIState.instance()
        states.update_requested = True

    @staticmethod
    def current() -> ToonPaletteUIState:
        states = ToonPaletteUIState.instance()
        states.update()

        return states

    @staticmethod
    @persistent
    def _sync_state(object: Scene):
        ToonPaletteUIState.request_update()

    @staticmethod
    def register():
        setattr(
            WindowManager,
            ToonPaletteUIState.PROP_NAME,
            PointerProperty(type=ToonPaletteUIState),
        )

        redo_post.append(ToonPaletteUIState._sync_state)
        undo_post.append(ToonPaletteUIState._sync_state)
        node_group_import_post.append(ToonPaletteUIState._sync_state)

    @staticmethod
    def unregister():
        delattr(WindowManager, ToonPaletteUIState.PROP_NAME)

        redo_post.remove(ToonPaletteUIState._sync_state)
        undo_post.remove(ToonPaletteUIState._sync_state)
        node_group_import_post.remove(ToonPaletteUIState._sync_state)
