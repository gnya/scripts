from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator

import bpy
from bpy.app.handlers import persistent, redo_post, undo_post
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import NodeTree, PropertyGroup, WindowManager

from toon.palette import (
    color_types,
    get_color,
    get_color_name,
    get_color_ptr,
    get_color_type,
    get_colors,
    get_group,
    get_group_name,
    get_palette,
    get_palette_name,
    get_palettes,
    get_texture_ptr,
    get_uv_map_ptr,
    set_color_name,
    set_color_type,
    set_group_name,
    set_palette_name,
    update_all_uv_pixel_snap,
)
from toon.utils import node_group_update_post

from .palette_node import ToonPaletteSearchIndex

if TYPE_CHECKING:
    from bpy.types import Scene

    from toon.palette import ToonPalette, ToonPaletteColor, ToonPaletteGroup


class ToonPaletteViewSettings(PropertyGroup):
    PROP_NAME = "toon_palette_view_settings"

    active_index: IntProperty(default=-1)

    show_expanded: BoolProperty(default=True)

    order: IntProperty(default=-1)

    @staticmethod
    def instance(id: NodeTree) -> ToonPaletteViewSettings:
        return getattr(id, ToonPaletteViewSettings.PROP_NAME)

    @staticmethod
    def register():
        setattr(
            NodeTree,
            ToonPaletteViewSettings.PROP_NAME,
            PointerProperty(type=ToonPaletteViewSettings),
        )

    @staticmethod
    def unregister():
        delattr(NodeTree, ToonPaletteViewSettings.PROP_NAME)


def get_view_settings(node_tree: NodeTree) -> ToonPaletteViewSettings:
    return ToonPaletteViewSettings.instance(node_tree)


class ToonPaletteUIItem(PropertyGroup):
    item_types = [("GROUP", "", ""), ("COLOR", "", "")]

    type: EnumProperty(items=item_types)

    node_tree: PointerProperty(type=NodeTree)

    socket_index: IntProperty(default=-1)

    def _get_group_name(self) -> str:
        return get_group_name(self.node_tree)

    def _set_group_name(self, value: str):
        set_group_name(self.node_tree, value)
        ToonPaletteSearchIndex.request_update()

    group_name: StringProperty(get=_get_group_name, set=_set_group_name)

    def _get_color_name(self) -> str:
        return get_color_name(self.node_tree, self.socket_index)

    def _set_color_name(self, value: str):
        set_color_name(self.node_tree, self.socket_index, value)

    color_name: StringProperty(get=_get_color_name, set=_set_color_name)

    def _get_color_type(self) -> int:
        return get_color_type(self.node_tree, self.socket_index)

    def _set_color_type(self, value: int):
        set_color_type(self.node_tree, self.socket_index, value)

    color_type: EnumProperty(
        name="Type",
        description="Type of color",
        items=color_types(),
        default="COLOR",
        get=_get_color_type,
        set=_set_color_type,
    )

    @property
    def color_ptr(self) -> tuple[Any, str]:
        return get_color_ptr(self.node_tree, self.socket_index)

    @property
    def texture_ptr(self) -> tuple[Any, str]:
        return get_texture_ptr(self.node_tree, self.socket_index)

    @property
    def uv_map_ptr(self) -> tuple[Any, str]:
        return get_uv_map_ptr(self.node_tree, self.socket_index)

    def _get_show_expanded(self) -> bool:
        return get_view_settings(self.node_tree).show_expanded

    def _set_show_expanded(self, value: bool):
        get_view_settings(self.node_tree).show_expanded = value

    show_expanded: BoolProperty(get=_get_show_expanded, set=_set_show_expanded)

    def _get_order(self) -> int:
        return get_view_settings(self.node_tree).order

    def _set_order(self, value: int):
        get_view_settings(self.node_tree).order = value

    order: IntProperty(get=_get_order, set=_set_order)

    header_index: IntProperty(default=-1)

    def group_data(self) -> ToonPaletteGroup | None:
        return get_group(self.node_tree)

    def colors_data(self) -> Iterator[ToonPaletteColor]:
        return get_colors(self.node_tree)

    def color_data(self) -> ToonPaletteColor | None:
        return get_color(self.node_tree, self.socket_index)

    def init(
        self, group: ToonPaletteGroup, color: ToonPaletteColor | None, header_index: int
    ):
        self.node_tree = group.node_tree
        self.header_index = header_index

        if color is None:
            self.type = "GROUP"
            self.socket_index = -1
        else:
            self.type = "COLOR"
            self.socket_index = color.socket_index

    @classmethod
    def register(cls):
        if update_all_uv_pixel_snap not in node_group_update_post:
            node_group_update_post.append(update_all_uv_pixel_snap)

    @staticmethod
    def unregister():
        if update_all_uv_pixel_snap in node_group_update_post:
            node_group_update_post.remove(update_all_uv_pixel_snap)


class ToonPaletteUIPaletteState(PropertyGroup):
    node_tree: PointerProperty(type=NodeTree)

    list_items: CollectionProperty(type=ToonPaletteUIItem)

    def _get_palette_name(self) -> str:
        return get_palette_name(self.node_tree)

    def _set_palette_name(self, value: str):
        set_palette_name(self.node_tree, value)
        ToonPaletteSearchIndex.request_update()

    palette_name: StringProperty(get=_get_palette_name, set=_set_palette_name)

    def _get_active_index(self) -> int:
        index = get_view_settings(self.node_tree).active_index
        index = min(index, len(self.list_items) - 1)

        if index < 0:
            return -1
        elif not (item := self.list_items[index]).show_expanded:
            return item.header_index
        else:
            return index

    def _set_active_index(self, value: int):
        get_view_settings(self.node_tree).active_index = value

    # TODO return: -1 ~ len(list_items) - 1
    active_index: IntProperty(get=_get_active_index, set=_set_active_index)

    def _get_show_expanded(self) -> bool:
        return get_view_settings(self.node_tree).show_expanded

    def _set_show_expanded(self, value: bool):
        get_view_settings(self.node_tree).show_expanded = value

    show_expanded: BoolProperty(get=_get_show_expanded, set=_set_show_expanded)

    def _get_order(self) -> int:
        return get_view_settings(self.node_tree).order

    def _set_order(self, value: int):
        get_view_settings(self.node_tree).order = value

    order: IntProperty(get=_get_order, set=_set_order)

    def active_item(self) -> ToonPaletteUIItem | None:
        if (index := self.active_index) < 0:
            return None
        else:
            return self.list_items[index]

    def palette_data(self) -> ToonPalette | None:
        return get_palette(self.node_tree)

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

            header_index += len(colors) + 1


class ToonPaletteUIState(PropertyGroup):
    PROP_NAME = "toon_palette_ui_state"

    list_states: CollectionProperty(type=ToonPaletteUIPaletteState)

    update_requested: BoolProperty(default=True)

    def update(self):
        if not self.update_requested:
            return

        self.list_states.clear()

        for palette in get_palettes():
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
            WindowManager,
            ToonPaletteUIState.PROP_NAME,
            PointerProperty(type=ToonPaletteUIState),
        )

        redo_post.append(ToonPaletteUIState._sync_state)
        undo_post.append(ToonPaletteUIState._sync_state)

    @staticmethod
    def unregister():
        delattr(WindowManager, ToonPaletteUIState.PROP_NAME)

        redo_post.remove(ToonPaletteUIState._sync_state)
        undo_post.remove(ToonPaletteUIState._sync_state)
