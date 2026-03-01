from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Literal, get_args

from toon.utils import unique_name

if TYPE_CHECKING:
    from bpy.types import BlendDataNodeTrees, NodeTree

_NODE_PREFIX = ".ToonPalette"
TOON_PALETTE_ORDER = "toon_palette_order"

ToonPaletteColorTypes = Literal["COLOR", "TEXTURE", "VECTOR", "VALUE"]


def color_type_to_int(type: ToonPaletteColorTypes) -> int:
    return get_args(ToonPaletteColorTypes).index(type)


def int_to_color_type(type: int) -> ToonPaletteColorTypes:
    return get_args(ToonPaletteColorTypes)[type]


def is_palette(node_tree: NodeTree):
    if node_tree is None:
        return False

    names = node_tree.name.split("|")

    return len(names) == 3 and names[0] == _NODE_PREFIX


def is_header(node_tree: NodeTree):
    if node_tree is None:
        return False

    names = node_tree.name.split("|")

    return len(names) == 3 and names[0] == _NODE_PREFIX and not names[2]


def is_group(node_tree: NodeTree):
    if node_tree is None:
        return False

    names = node_tree.name.split("|")

    return len(names) == 3 and names[0] == _NODE_PREFIX and names[2]


def get_palette_name(node_tree: NodeTree) -> str:
    if is_palette(node_tree):
        return node_tree.name.split("|", 2)[1]
    else:
        return ""


def get_group_name(node_tree: NodeTree) -> str:
    if is_group(node_tree):
        return node_tree.name.split("|", 2)[2]
    else:
        return ""


def get_order(node_tree: NodeTree) -> int:
    if is_palette(node_tree):
        settings = getattr(node_tree, TOON_PALETTE_ORDER)

        if settings is not None:
            return settings.order

    return -1


def set_order(node_tree: NodeTree, value: int):
    if is_palette(node_tree):
        settings = getattr(node_tree, TOON_PALETTE_ORDER)

        if settings is not None:
            settings.order = value


def order_to_key(order: int) -> tuple[bool, int]:
    return order == -1, order


def filter_node_trees(
    node_groups: BlendDataNodeTrees, palette_name: str = ""
) -> Iterator[NodeTree]:
    if palette_name == "":
        for node_tree in node_groups:
            if is_palette(node_tree):
                yield node_tree
    else:
        for node_tree in node_groups:
            if get_palette_name(node_tree) == palette_name:
                yield node_tree


def _palette_names(node_groups: BlendDataNodeTrees) -> list[str]:
    palette_names = []

    for node_tree in filter_node_trees(node_groups):
        _, palette_name, group_name = node_tree.name.split("|", 2)

        if group_name == "":
            palette_names.append(palette_name)

    return palette_names


def resolve_group_name(name: str) -> str:
    if name == "":
        return "Group"
    else:
        return name.replace("|", "_")


def resolve_palette_name(node_groups: BlendDataNodeTrees, name: str) -> str:
    if name == "":
        name = "Palette"
    else:
        name = name.replace("|", "_")

    return unique_name(_palette_names(node_groups), name)


def build_node_tree_name(palette_name: str, group_name: str) -> str:
    return "|".join([_NODE_PREFIX, palette_name, group_name])
