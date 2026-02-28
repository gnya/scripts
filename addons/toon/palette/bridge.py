from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator, get_args

import bpy

from .color import ToonPaletteColor
from .group import ToonPaletteGroup
from .model import ToonPaletteFacade
from .palette import ToonPalette
from .utils import (
    ToonPaletteColorTypes,
    color_type_to_int,
    get_palette_name,
    int_to_color_type,
    is_group,
    is_palette,
)

if TYPE_CHECKING:
    from bpy.types import NodeTree


def _get_palette_by_name(name: str):
    return ToonPaletteFacade(bpy.data.node_groups).get(name)


def get_palette(node_tree: NodeTree) -> ToonPalette | None:
    if is_palette(node_tree):
        return _get_palette_by_name(get_palette_name(node_tree))
    else:
        return None


def set_palette_name(node_tree: NodeTree, value: str):
    if (palette := get_palette(node_tree)) is not None:
        palette.name = value


def set_group_name(node_tree: NodeTree, value: str):
    if is_group(node_tree):
        ToonPaletteGroup(node_tree).name = value


def get_color_name(node_tree: NodeTree, index: int) -> str:
    if is_group(node_tree):
        return ToonPaletteColor(node_tree, index).name
    else:
        return ""


def set_color_name(node_tree: NodeTree, index: int, value: str):
    if is_group(node_tree):
        ToonPaletteColor(node_tree, index).name = value


def color_types() -> list[tuple[str, str, str]]:
    args = get_args(ToonPaletteColorTypes)

    return [(t, t.capitalize(), "") for t in args]


def get_color_type(node_tree: NodeTree, index: int) -> int:
    if is_group(node_tree):
        return color_type_to_int(ToonPaletteColor(node_tree, index).type)
    else:
        return -1


def set_color_type(node_tree: NodeTree, index: int, value: int):
    if is_group(node_tree):
        ToonPaletteColor(node_tree, index).type = int_to_color_type(value)


def get_color_ptr(node_tree: NodeTree, index: int) -> tuple[Any, str]:
    if is_group(node_tree):
        return ToonPaletteColor(node_tree, index).color_ptr
    else:
        return None, ""


def get_texture_ptr(node_tree: NodeTree, index: int) -> tuple[Any, str]:
    if is_group(node_tree):
        return ToonPaletteColor(node_tree, index).texture_ptr
    else:
        return None, ""


def get_uv_map_ptr(node_tree: NodeTree, index: int) -> tuple[Any, str]:
    if is_group(node_tree):
        return ToonPaletteColor(node_tree, index).uv_map_ptr
    else:
        return None, ""


def get_group(node_tree: NodeTree) -> ToonPaletteGroup | None:
    if is_group(node_tree):
        return ToonPaletteGroup(node_tree)
    else:
        return None


def get_color(node_tree: NodeTree, index: int) -> ToonPaletteColor | None:
    if is_group(node_tree):
        return ToonPaletteColor(node_tree, index)
    else:
        return None


def update_all_uv_pixel_snap(node_tree: NodeTree):
    if is_group(node_tree):
        group = ToonPaletteGroup(node_tree)

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


def get_colors(node_tree: NodeTree) -> Iterator[ToonPaletteColor]:
    if (group := get_group(node_tree)) is not None:
        yield from group.colors()


def get_palettes() -> Iterator[ToonPalette]:
    yield from ToonPaletteFacade(bpy.data.node_groups).palettes()


def get_node_tree(palette_name: str, group_name: str = "") -> NodeTree | None:
    if (palette := _get_palette_by_name(palette_name)) is None:
        return None
    elif (group := palette.get(group_name)) is None:
        return palette.header
    else:
        return group.node_tree
