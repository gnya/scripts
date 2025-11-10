import bpy

from bpy.types import NodeTree, PropertyGroup
from bpy.props import (
    BoolProperty, CollectionProperty, EnumProperty, FloatVectorProperty
)

from toon.utils import make_unique_name

from .props_base import DataCollection
from .props_socket import SocketLinkedItemBase


class PaletteItem(SocketLinkedItemBase, PropertyGroup):
    item_types = [
        ('COLOR', 'Color', ''),
        ('TEXTURE', 'Texture', ''),
        ('MIX', 'Mix', '')
    ]

    def update_type(self, context):
        pass

    def update_color(self, context):
        self.socket.default_value = self.color

    type: EnumProperty(
        items=item_types, default='COLOR',
        update=update_type
    )

    color: FloatVectorProperty(
        subtype='COLOR', size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        soft_min=0.0, soft_max=1.0,
        update=update_color
    )

    @property
    def node_tree(self) -> NodeTree:
        return self.id_data

    def parent_keys(self):
        path = self.path_from_id().rsplit('.', 1)[0]
        parent = self.id_data.path_resolve(path)

        return parent.items.keys()

    def linked_items(self):
        for group in self.id_data.toon_palette.items:
            for item in group.items:
                yield item


class PaletteGroup(DataCollection, PropertyGroup):
    items: CollectionProperty(type=PaletteItem)

    def parent_keys(self):
        return self.id_data.toon_palette.items.keys()

    def on_rename(self):
        pass


class Palette(DataCollection, PropertyGroup):
    items: CollectionProperty(type=PaletteGroup)

    is_available: BoolProperty(default=False)

    def parent_keys(self):
        names = []

        for node_tree in bpy.data.node_groups:
            if node_tree.toon_palette.is_available:
                names.append(node_tree.toon_palette.name)

        return names

    def on_rename(self):
        pass

    @staticmethod
    def new(name: str) -> 'Palette':
        node_tree = bpy.data.node_groups.new('.TOON_PALETTE', 'ShaderNodeTree')

        palette = node_tree.toon_palette
        palette.name = make_unique_name(name, palette.parent_keys())
        palette.is_available = True

        return palette

    @staticmethod
    def remove(palette: 'Palette'):
        bpy.data.node_groups.remove(palette.id_data)
