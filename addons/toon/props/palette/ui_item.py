from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator

from bpy.props import (
    BoolProperty,
    EnumProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import NodeTree, PropertyGroup

from toon.palette import (
    color_types,
    get_color,
    get_color_name,
    get_color_ptr,
    get_color_type,
    get_colors,
    get_group,
    get_group_name,
    get_library,
    get_palette,
    get_texture_ptr,
    get_uv_map_ptr,
    set_color_name,
    set_color_type,
    set_group_name,
    update_all_uv_pixel_snap,
)
from toon.utils import node_group_update_post

from .node import ToonPaletteSearchIndex
from .view import get_show_expanded, set_show_expanded

if TYPE_CHECKING:
    from toon.palette import ToonPalette, ToonPaletteColor, ToonPaletteGroup


class ToonPaletteUIItem(PropertyGroup):
    item_types = [("GROUP", "", ""), ("COLOR", "", "")]

    type: EnumProperty(items=item_types)

    node_tree: PointerProperty(type=NodeTree)

    group_index: IntProperty(default=-1)

    color_index: IntProperty(default=-1)
    """
    NOTE If `type` is `COLOR`, this variable matches `socket_index`.
    """

    def _get_group_name(self) -> str:
        return get_group_name(self.node_tree)

    def _set_group_name(self, value: str):
        set_group_name(self.node_tree, value)
        ToonPaletteSearchIndex.request_update()

    group_name: StringProperty(get=_get_group_name, set=_set_group_name)

    def _get_color_name(self) -> str:
        return get_color_name(self.node_tree, self.color_index)

    def _set_color_name(self, value: str):
        set_color_name(self.node_tree, self.color_index, value)

    color_name: StringProperty(get=_get_color_name, set=_set_color_name)

    def _get_color_type(self) -> int:
        return get_color_type(self.node_tree, self.color_index)

    def _set_color_type(self, value: int):
        set_color_type(self.node_tree, self.color_index, value)

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
        return get_color_ptr(self.node_tree, self.color_index)

    @property
    def texture_ptr(self) -> tuple[Any, str]:
        return get_texture_ptr(self.node_tree, self.color_index)

    @property
    def uv_map_ptr(self) -> tuple[Any, str]:
        return get_uv_map_ptr(self.node_tree, self.color_index)

    def _get_show_expanded(self) -> bool:
        return get_show_expanded(self.node_tree)

    def _set_show_expanded(self, value: bool):
        set_show_expanded(self.node_tree, value)

    show_expanded: BoolProperty(get=_get_show_expanded, set=_set_show_expanded)

    header_index: IntProperty(default=-1)

    def is_linked(self) -> bool:
        return get_library(self.node_tree) != ""

    def palette_data(self) -> ToonPalette | None:
        return get_palette(self.node_tree)

    def group_data(self) -> ToonPaletteGroup | None:
        return get_group(self.node_tree)

    def colors_data(self) -> Iterator[ToonPaletteColor]:
        return get_colors(self.node_tree)

    def color_data(self) -> ToonPaletteColor | None:
        return get_color(self.node_tree, self.color_index)

    def init(
        self,
        group: ToonPaletteGroup,
        group_index: int,
        header_index: int,
        color: ToonPaletteColor | None = None,
    ):
        self.node_tree = group.node_tree
        self.group_index = group_index
        self.header_index = header_index

        if color is None:
            self.type = "GROUP"
            self.color_index = -1
        else:
            self.type = "COLOR"
            self.color_index = color.socket_index

    @classmethod
    def register(cls):
        if update_all_uv_pixel_snap not in node_group_update_post:
            node_group_update_post.append(update_all_uv_pixel_snap)

    @staticmethod
    def unregister():
        if update_all_uv_pixel_snap in node_group_update_post:
            node_group_update_post.remove(update_all_uv_pixel_snap)
