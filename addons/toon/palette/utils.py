from __future__ import annotations

from re import sub
from typing import TYPE_CHECKING, Iterator, Literal, get_args

import bpy

if TYPE_CHECKING:
    from bpy.types import NodeTree

TOON_PALETTE_PREFIX = ".ToonPalette"

ToonPaletteColorTypes = Literal["COLOR", "TEXTURE", "VECTOR", "VALUE"]


def color_type_to_int(type: ToonPaletteColorTypes) -> int:
    return get_args(ToonPaletteColorTypes).index(type)


def int_to_color_type(type: int) -> ToonPaletteColorTypes:
    return get_args(ToonPaletteColorTypes)[type]


def is_palette(node_tree: NodeTree):
    names = node_tree.name.split("|")

    return len(names) == 3 and names[0] == TOON_PALETTE_PREFIX


def get_palette_name(node_tree: NodeTree) -> str:
    if is_palette(node_tree):
        return node_tree.name.split("|", 2)[1]
    else:
        return ""


def get_group_name(node_tree: NodeTree) -> str:
    if is_palette(node_tree):
        return node_tree.name.split("|", 2)[2]
    else:
        return ""


def filter_node_trees(palette_name: str = "") -> Iterator[NodeTree]:
    for node_tree in bpy.data.node_groups:
        if is_palette(node_tree):
            if palette_name == "":
                yield node_tree
            else:
                names = node_tree.name.split("|", 2)

                if names[1] == palette_name:
                    yield node_tree


def _group_names() -> list[str]:
    group_names = []

    for node_tree in filter_node_trees():
        names = node_tree.name.split("|", 2)

        if names[2] == "":
            group_names.append(names[1])

    return group_names


def _make_unique_name(name: str, names: list[str]) -> str:
    base = sub(r".\d{3}$", "", name)
    i = 1

    while name in names:
        name = f"{base}.{i:03d}"
        i += 1

    return name


def build_node_tree_name(
    palette_name: str, group_name: str, unique: bool = False
) -> str:
    if unique:
        palette_name = _make_unique_name(palette_name, _group_names())

    return "|".join([TOON_PALETTE_PREFIX, palette_name, group_name])
