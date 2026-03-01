from __future__ import annotations

import bpy
from bpy.props import BoolProperty, IntProperty, PointerProperty
from bpy.types import NodeTree, PropertyGroup, WindowManager


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
        setattr(
            WindowManager,
            ToonPaletteViewSettings.PROP_NAME,
            PointerProperty(type=ToonPaletteViewSettings),
        )

    @staticmethod
    def unregister():
        delattr(NodeTree, ToonPaletteViewSettings.PROP_NAME)
        delattr(WindowManager, ToonPaletteViewSettings.PROP_NAME)


def get_view_settings(id: NodeTree) -> ToonPaletteViewSettings:
    return getattr(id, ToonPaletteViewSettings.PROP_NAME)


def get_default_view_settings() -> ToonPaletteViewSettings:
    id = bpy.context.window_manager

    return getattr(id, ToonPaletteViewSettings.PROP_NAME)
