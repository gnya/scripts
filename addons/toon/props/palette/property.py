from __future__ import annotations

from bpy.props import IntProperty, PointerProperty
from bpy.types import NodeTree, PropertyGroup

from toon.palette import IToonPaletteProperty


class ToonPaletteProperty(PropertyGroup, IToonPaletteProperty):
    order: IntProperty(default=-1)

    @staticmethod
    def register():
        setattr(
            NodeTree,
            ToonPaletteProperty.PROP_NAME,
            PointerProperty(type=ToonPaletteProperty),
        )

    @staticmethod
    def unregister():
        delattr(NodeTree, ToonPaletteProperty.PROP_NAME)
