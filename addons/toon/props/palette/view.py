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


def get_view_settings(id: NodeTree | None) -> ToonPaletteViewSettings:
    if id is None:
        default_id = bpy.context.window_manager

        return getattr(default_id, ToonPaletteViewSettings.PROP_NAME)
    else:
        return getattr(id, ToonPaletteViewSettings.PROP_NAME)


def get_active_index(node_tree: NodeTree | None) -> int:
    return get_view_settings(node_tree).active_index


def set_active_index(node_tree: NodeTree | None, value: int):
    get_view_settings(node_tree).active_index = value


def get_show_expanded(node_tree: NodeTree | None) -> bool:
    return get_view_settings(node_tree).show_expanded


def set_show_expanded(node_tree: NodeTree | None, value: bool):
    get_view_settings(node_tree).show_expanded = value
