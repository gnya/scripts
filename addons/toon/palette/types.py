from __future__ import annotations

from typing import TYPE_CHECKING, Literal, get_args

from .naming import is_palette

if TYPE_CHECKING:
    from bpy.types import NodeTree

ToonPaletteColorTypes = Literal["COLOR", "TEXTURE", "VECTOR", "VALUE"]


class IToonPaletteProperty:
    PROP_NAME = "toon_palette_property"

    order: int


def color_type_to_int(type: ToonPaletteColorTypes) -> int:
    return get_args(ToonPaletteColorTypes).index(type)


def int_to_color_type(type: int) -> ToonPaletteColorTypes:
    return get_args(ToonPaletteColorTypes)[type]


def get_property(node_tree: NodeTree) -> IToonPaletteProperty:
    if (prop := getattr(node_tree, IToonPaletteProperty.PROP_NAME, None)) is None:
        raise NotImplementedError()
    else:
        return prop


def get_order(node_tree: NodeTree) -> int:
    if is_palette(node_tree):
        return get_property(node_tree).order
    else:
        return -1


def set_order(node_tree: NodeTree, value: int):
    if is_palette(node_tree):
        get_property(node_tree).order = value


def order_to_key(order: int) -> tuple[bool, int]:
    return order == -1, order
