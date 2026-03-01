from __future__ import annotations

from bpy.props import BoolProperty, IntProperty, PointerProperty
from bpy.types import NodeTree, PropertyGroup


class ToonPaletteViewSettings(PropertyGroup):
    PROP_NAME = "toon_palette_view_settings"

    active_index: IntProperty(default=-1)

    show_expanded: BoolProperty(default=True)

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
    return getattr(node_tree, ToonPaletteViewSettings.PROP_NAME)
