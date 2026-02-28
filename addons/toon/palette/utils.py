from __future__ import annotations

from re import sub
from typing import TYPE_CHECKING, Iterator, Literal, get_args

if TYPE_CHECKING:
    from bpy.types import BlendDataNodeTrees, NodeTree

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


def filter_node_trees(
    node_groups: BlendDataNodeTrees, palette_name: str = ""
) -> Iterator[NodeTree]:
    for node_tree in node_groups:
        if is_palette(node_tree):
            if palette_name == "":
                yield node_tree
            else:
                names = node_tree.name.split("|", 2)

                if names[1] == palette_name:
                    yield node_tree


def _palette_names(node_groups: BlendDataNodeTrees) -> list[str]:
    palette_names = []

    for node_tree in filter_node_trees(node_groups):
        names = node_tree.name.split("|", 2)

        if names[2] == "":
            palette_names.append(names[1])

    return palette_names


def _make_unique_name(name: str, names: list[str]) -> str:
    base = sub(r".\d{3}$", "", name)
    i = 1

    while name in names:
        name = f"{base}.{i:03d}"
        i += 1

    return name


def build_node_tree_name(
    palette_name: str,
    group_name: str,
    unique_palette_name: bool = False,
    node_groups: BlendDataNodeTrees = None,
) -> str:
    if unique_palette_name and node_groups is not None:
        palette_name = _make_unique_name(palette_name, _palette_names(node_groups))

    return "|".join([TOON_PALETTE_PREFIX, palette_name, group_name])
