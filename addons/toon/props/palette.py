from __future__ import annotations

from bpy.props import IntProperty, PointerProperty
from bpy.types import NodeTree, PropertyGroup

from toon.palette import TOON_PALETTE_ORDER


class ToonPaletteOrder(PropertyGroup):
    order: IntProperty(default=-1)

    @staticmethod
    def register():
        setattr(NodeTree, TOON_PALETTE_ORDER, PointerProperty(type=ToonPaletteOrder))

    @staticmethod
    def unregister():
        delattr(NodeTree, TOON_PALETTE_ORDER)
