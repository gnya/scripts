from __future__ import annotations

import bpy

from bpy.props import CollectionProperty, PointerProperty
from bpy.types import NodeTree, PropertyGroup, WindowManager


NODE_TREE_NAME = '.ToonPalette'


def build_node_tree_name(palette_name: str, group_name: str) -> str:
    return '|'.join([
        NODE_TREE_NAME,
        palette_name,
        group_name
    ])


class ToonPaletteColor(PropertyGroup):
    pass


class ToonPaletteGroup(PropertyGroup):
    colors: CollectionProperty(type=ToonPaletteColor)


class ToonPalette(PropertyGroup):
    groups: CollectionProperty(type=ToonPaletteGroup)

    def add(self, group_name: str):
        node_tree_name = build_node_tree_name(self.name, group_name)
        node_tree = bpy.data.node_groups.new(node_tree_name, 'ShaderNodeTree')
        node_tree.use_fake_user = True

    def remove(self, group_name: str):
        node_tree_name = build_node_tree_name(self.name, group_name)
        node_tree = bpy.data.node_groups.get(node_tree_name)

        if node_tree is not None:
            bpy.data.node_groups.remove(node_tree)


class ToonPaletteFacade(PropertyGroup):
    PROP_NAME = 'toon_palette_facade'

    palettes: CollectionProperty(type=ToonPalette)

    def get_node_tree(self, palette_name: str, group_name: str) -> NodeTree | None:
        node_tree_name = build_node_tree_name(palette_name, group_name)

        return bpy.data.node_groups.get(node_tree_name)

    def add(self, palette_name: str):
        node_tree_name = build_node_tree_name(palette_name, 'Group')
        node_tree = bpy.data.node_groups.new(node_tree_name, 'ShaderNodeTree')
        node_tree.use_fake_user = True

    def remove(self, palette_name: str):
        node_tree_name = build_node_tree_name(palette_name, '')

        for node_tree in list(bpy.data.node_groups):
            if node_tree.name.startswith(node_tree_name):
                bpy.data.node_groups.remove(node_tree)

    def update(self):
        self.palettes.clear()
        palette = None

        for node_tree in bpy.data.node_groups:
            name = node_tree.name

            if not name.startswith(NODE_TREE_NAME):
                continue

            _, palette_name, group_name = name.split('|', 2)

            if palette is None or palette.name != palette_name:
                palette = self.palettes.add()
                palette.name = palette_name

            group = palette.groups.add()
            group.name = group_name

    @staticmethod
    def instance() -> ToonPaletteFacade:
        id = bpy.context.window_manager

        return getattr(id, ToonPaletteFacade.PROP_NAME)

    @staticmethod
    def register():
        setattr(
            WindowManager, ToonPaletteFacade.PROP_NAME,
            PointerProperty(type=ToonPaletteFacade)
        )

    @staticmethod
    def unregister():
        delattr(WindowManager, ToonPaletteFacade.PROP_NAME)
