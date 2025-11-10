import bpy

from bpy.app import handlers, timers
from bpy.types import NodeTree, PropertyGroup, WindowManager
from bpy.props import (
    BoolProperty, CollectionProperty, PointerProperty
)

from toon.utils import make_unique_name

from .base import DataCollection
from .item import PaletteItem


class PaletteGroup(DataCollection, PropertyGroup):
    items: CollectionProperty(type=PaletteItem)

    def parent_keys(self):
        palette = getattr(self.id_data, Palette.PROP_NAME)

        return palette.items.keys()

    def on_rename(self):
        pass


class PaletteName(PropertyGroup):
    PROP_NAME = 'toon_palette_names'

    @staticmethod
    def prop_data():
        return bpy.context.window_manager

    @staticmethod
    def update():
        data = PaletteName.prop_data()
        names = getattr(data, PaletteName.PROP_NAME)
        names.clear()

        for palette in Palette.instances():
            names.add().name = palette.name

    @staticmethod
    @handlers.persistent
    def _load_post(scene):
        PaletteName.update()

    @staticmethod
    def register():
        setattr(
            WindowManager, PaletteName.PROP_NAME,
            CollectionProperty(type=PaletteName)
        )

        handlers.load_post.append(PaletteName._load_post)
        timers.register(PaletteName.update, first_interval=0.1)

    @staticmethod
    def unregister():
        delattr(WindowManager, PaletteName.PROP_NAME)

        handlers.load_post.remove(PaletteName.update)


class Palette(DataCollection, PropertyGroup):
    NODE_TREE_NAME = '.TOON_PALETTE'
    PROP_NAME = 'toon_palette'

    items: CollectionProperty(type=PaletteGroup)

    is_available: BoolProperty(default=False)

    def parent_keys(self):
        names = []

        for palette in Palette.instances():
            names.append(palette.name)

        return names

    def on_rename(self):
        PaletteName.update()

    @staticmethod
    def new(name: str) -> 'Palette':
        node_tree = bpy.data.node_groups.new(
            Palette.NODE_TREE_NAME, 'ShaderNodeTree'
        )
        node_tree.use_fake_user = True

        palette = getattr(node_tree, Palette.PROP_NAME)
        name = make_unique_name(name, palette.parent_keys())
        palette.name = name
        palette.is_available = True

        PaletteName.update()

        return palette

    @staticmethod
    def remove(palette: 'Palette'):
        bpy.data.node_groups.remove(palette.id_data)

        PaletteName.update()

    @staticmethod
    def instances():
        for node_tree in bpy.data.node_groups:
            palette = getattr(node_tree, Palette.PROP_NAME)

            if palette.is_available:
                yield palette

    @classmethod
    def register(cls):
        setattr(
            NodeTree, Palette.PROP_NAME,
            PointerProperty(type=cls)
        )

    @staticmethod
    def unregister(cls):
        delattr(NodeTree, Palette.PROP_NAME)
