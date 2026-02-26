from __future__ import annotations
from typing import Any, Iterator

import bpy

from bpy.app.handlers import persistent, redo_post, undo_post
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    IntProperty,
    PointerProperty,
    StringProperty
)
from bpy.types import NodeTree, PropertyGroup, Scene, WindowManager

from toon.palette import ToonPaletteColor
from toon.palette import ToonPaletteGroup
from toon.palette import ToonPalette
from toon.palette import ToonPaletteFacade
from toon.palette import color_type_to_int
from toon.palette import int_to_color_type
from toon.palette import get_palette_name
from toon.palette import get_group_name
from toon.utils import node_group_update_post

from .palette_node import ToonPaletteSearchIndex


class ToonPaletteViewSettings(PropertyGroup):
    PROP_NAME = 'toon_palette_view_settings'

    active_index: IntProperty(default=-1)

    show_expanded: BoolProperty(default=True)

    @staticmethod
    def instance(id: NodeTree) -> ToonPaletteViewSettings:
        return getattr(id, ToonPaletteViewSettings.PROP_NAME)

    @staticmethod
    def register():
        setattr(
            NodeTree, ToonPaletteViewSettings.PROP_NAME,
            PointerProperty(type=ToonPaletteViewSettings)
        )

    @staticmethod
    def unregister():
        delattr(NodeTree, ToonPaletteViewSettings.PROP_NAME)


class ToonPaletteUIItem(PropertyGroup):
    item_types = [
        ('GROUP', '', ''),
        ('COLOR', '', '')
    ]

    type: EnumProperty(items=item_types)

    node_tree: PointerProperty(type=NodeTree)

    socket_index: IntProperty(default=-1)

    def _get_group_name(self) -> str:
        return get_group_name(self.node_tree)

    def _set_group_name(self, value: str):
        group = ToonPaletteGroup.from_node_tree(self.node_tree)

        if group is not None:
            group.name = value

            ToonPaletteSearchIndex.request_update()

    group_name: StringProperty(
        get=_get_group_name, set=_set_group_name
    )

    def _get_color_name(self) -> str:
        if (color := self.color_data()) is not None:
            return color.name
        else:
            return ''

    def _set_color_name(self, value: str):
        if (color := self.color_data()) is not None:
            color.name = value
        else:
            pass

    color_name: StringProperty(
        get=_get_color_name, set=_set_color_name
    )

    color_types = [
        ('COLOR', 'Color', ''),
        ('TEXTURE', 'Texture', ''),
        ('VECTOR', 'Vector', ''),
        ('VALUE', 'Value', '')
    ]

    def _get_color_type(self) -> int:
        if (color := self.color_data()) is not None:
            return color_type_to_int(color.type)
        else:
            return -1

    def _set_color_type(self, value: int):
        if (color := self.color_data()) is not None:
            color.type = int_to_color_type(value)
        else:
            pass

    color_type: EnumProperty(
        name='Type', description='Type of color',
        items=color_types, default='COLOR',
        get=_get_color_type, set=_set_color_type
    )

    @property
    def color_ptr(self) -> tuple[Any, str]:
        if (color := self.color_data()) is not None:
            return color.color_ptr
        else:
            return None, ''

    @property
    def texture_ptr(self) -> tuple[Any, str]:
        if (color := self.color_data()) is not None:
            return color.texture_ptr
        else:
            return None, ''

    @property
    def uv_map_ptr(self) -> tuple[Any, str]:
        if (color := self.color_data()) is not None:
            return color.uv_map_ptr
        else:
            return None, ''

    def _view_settings(self) -> ToonPaletteViewSettings:
        return ToonPaletteViewSettings.instance(self.node_tree)

    def _get_show_expanded(self) -> bool:
        return self._view_settings().show_expanded

    def _set_show_expanded(self, value: bool):
        self._view_settings().show_expanded = value

    show_expanded: BoolProperty(
        get=_get_show_expanded, set=_set_show_expanded
    )

    header_index: IntProperty(default=-1)

    def group_data(self) -> ToonPaletteGroup | None:
        return ToonPaletteGroup.from_node_tree(self.node_tree)

    def colors_data(self) -> Iterator[ToonPaletteColor]:
        group = self.group_data()

        if group is not None:
            yield from group.colors()

    def color_data(self) -> ToonPaletteColor | None:
        if self.type != 'COLOR' or self.socket_index < 0:
            return None

        return ToonPaletteColor(self.socket_index, self.node_tree)

    def init(self, group: ToonPaletteGroup, color: ToonPaletteColor | None, header_index: int):
        self.node_tree = group.node_tree
        self.header_index = header_index

        if color is None:
            self.type = 'GROUP'
        else:
            self.type = 'COLOR'
            self.socket_index = color.socket_index

    @staticmethod
    def _update_texture_uv_snap(node_tree: NodeTree):
        group = ToonPaletteGroup.from_node_tree(node_tree)

        if group is None:
            return

        for color in group.colors():
            data, prop = color.texture_ptr

            if data is None:
                continue

            tex = getattr(data, prop)

            if tex is None:
                continue

            (data_w, prop_w), (data_h, prop_h) = color.uv_pixel_snap_ptr

            if data_w is None or data_h is None:
                continue

            setattr(data_w, prop_w, tex.size[0])
            setattr(data_h, prop_h, tex.size[1])

    @classmethod
    def register(cls):
        if ToonPaletteUIItem._update_texture_uv_snap not in node_group_update_post:
            node_group_update_post.append(ToonPaletteUIItem._update_texture_uv_snap)

    @staticmethod
    def unregister():
        if ToonPaletteUIItem._update_texture_uv_snap in node_group_update_post:
            node_group_update_post.remove(ToonPaletteUIItem._update_texture_uv_snap)


class ToonPaletteUIPaletteState(PropertyGroup):
    node_tree: PointerProperty(type=NodeTree)

    list_items: CollectionProperty(type=ToonPaletteUIItem)

    def _get_palette_name(self) -> str:
        return get_palette_name(self.node_tree)

    def _set_palette_name(self, value: str):
        palette = ToonPalette.from_node_tree(self.node_tree)

        if palette is not None:
            palette.name = value

            ToonPaletteSearchIndex.request_update()

    palette_name: StringProperty(
        get=_get_palette_name, set=_set_palette_name
    )

    def _view_settings(self) -> ToonPaletteViewSettings:
        return ToonPaletteViewSettings.instance(self.node_tree)

    def _get_active_index(self) -> int:
        index = self._view_settings().active_index
        index = min(index, len(self.list_items) - 1)

        if index < 0:
            return -1
        elif not (item := self.list_items[index]).show_expanded:
            return item.header_index
        else:
            return index

    def _set_active_index(self, value: int):
        self._view_settings().active_index = value

    def _get_show_expanded(self) -> bool:
        return self._view_settings().show_expanded

    def _set_show_expanded(self, value: bool):
        self._view_settings().show_expanded = value

    # TODO return: -1 ~ len(list_items) - 1
    active_index: IntProperty(
        get=_get_active_index, set=_set_active_index
    )

    show_expanded: BoolProperty(
        get=_get_show_expanded, set=_set_show_expanded
    )

    def active_item(self) -> ToonPaletteUIItem | None:
        if (index := self.active_index) < 0:
            return None
        else:
            return self.list_items[index]

    def init(self, palette: ToonPalette):
        self.node_tree = palette.header
        header_index = 0

        for group in palette.groups():
            item = self.list_items.add()
            item.init(group, None, header_index)
            colors = list(group.colors())

            for color in colors:
                item = self.list_items.add()
                item.init(group, color, header_index)

            header_index += len(colors)

    def palette_data(self) -> ToonPalette | None:
        return ToonPalette.from_node_tree(self.node_tree)


class ToonPaletteUIState(PropertyGroup):
    PROP_NAME = 'toon_palette_ui_state'

    list_states: CollectionProperty(type=ToonPaletteUIPaletteState)

    update_requested: BoolProperty(default=True)

    def update(self):
        if not self.update_requested:
            return

        self.list_states.clear()

        for palette in ToonPaletteFacade.palettes():
            # TODO Consider orphan groups.
            if palette.header is not None:
                state = self.list_states.add()
                state.init(palette)

        self.update_requested = False

    @staticmethod
    def _instance() -> ToonPaletteUIState:
        id = bpy.context.window_manager

        return getattr(id, ToonPaletteUIState.PROP_NAME)

    @staticmethod
    def request_update():
        states = ToonPaletteUIState._instance()
        states.update_requested = True

    @staticmethod
    def current_states() -> Iterator[ToonPaletteUIPaletteState]:
        states = ToonPaletteUIState._instance()
        states.update()

        for state in states.list_states:
            yield state

    # TODO blend_import_post (Call it when append node trees.)
    @staticmethod
    @persistent
    def _sync_state(object: Scene):
        ToonPaletteUIState.request_update()

    @staticmethod
    def register():
        setattr(
            WindowManager, ToonPaletteUIState.PROP_NAME,
            PointerProperty(type=ToonPaletteUIState)
        )

        redo_post.append(ToonPaletteUIState._sync_state)
        undo_post.append(ToonPaletteUIState._sync_state)

    @staticmethod
    def unregister():
        delattr(WindowManager, ToonPaletteUIState.PROP_NAME)

        redo_post.remove(ToonPaletteUIState._sync_state)
        undo_post.remove(ToonPaletteUIState._sync_state)
