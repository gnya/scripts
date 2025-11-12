import bpy

from bpy.app import handlers, timers
from bpy.props import (
    BoolProperty, CollectionProperty, PointerProperty
)
from bpy.types import NodeTree, PropertyGroup, Scene, WindowManager

from toon.utils import override
from toon.utils.group import EntryBase, Group

from .entry import PaletteEntry


class PaletteGroup(Group, PropertyGroup):
    items: CollectionProperty(type=PaletteEntry)


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
    def _load_post(scene: Scene):
        PaletteName.update()

    @staticmethod
    def register():
        setattr(
            WindowManager, PaletteName.PROP_NAME,
            CollectionProperty(type=PaletteName)
        )

        if PaletteName.update not in handlers.load_post:
            handlers.load_post.append(PaletteName._load_post)

        timers.register(PaletteName.update, first_interval=0.1)

    @staticmethod
    def unregister():
        delattr(WindowManager, PaletteName.PROP_NAME)

        if PaletteName.update in handlers.load_post:
            handlers.load_post.remove(PaletteName._load_post)


class Palette(Group, PropertyGroup):
    NODE_TREE_NAME = '.TOON_PALETTE'
    PROP_NAME = 'toon_palette'

    items: CollectionProperty(type=PaletteGroup)

    is_available: BoolProperty(default=False)

    @override
    def parent(self) -> tuple[list[str], list[EntryBase]]:
        names = []
        items = []

        for palette in Palette.instances():
            names.append(palette.name)
            items.append(palette)

        return names, items

    @override
    def on_rename(self):
        PaletteName.update()

    @staticmethod
    def new_instance(name: str) -> 'Palette':
        node_tree = bpy.data.node_groups.new(
            Palette.NODE_TREE_NAME, 'ShaderNodeTree'
        )
        node_tree.use_fake_user = True

        palette = getattr(node_tree, Palette.PROP_NAME)
        palette.is_available = True
        palette.name = name

        PaletteName.update()

        return palette

    @staticmethod
    def del_instance(palette: 'Palette'):
        bpy.data.node_groups.remove(palette.id_data)

        PaletteName.update()

    @staticmethod
    def instances():
        for node_tree in bpy.data.node_groups:
            palette = getattr(node_tree, Palette.PROP_NAME)

            if palette.is_available:
                yield palette

    @staticmethod
    def instance(name: str):
        for palette in Palette.instances():
            if palette.name == name:
                return palette

        return None

    @classmethod
    def register(cls):
        setattr(
            NodeTree, Palette.PROP_NAME,
            PointerProperty(type=cls)
        )

    @staticmethod
    def unregister():
        delattr(NodeTree, Palette.PROP_NAME)
