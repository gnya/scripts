from bpy.types import PropertyGroup
from bpy.props import (
    CollectionProperty, EnumProperty, FloatVectorProperty
)

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
    def node_tree(self):
        return self.id_data

    def linked_items(self):
        for group in self.id_data.toon_palette.items:
            for item in group.items:
                yield item


class PaletteGroup(DataCollection, PropertyGroup):
    items: CollectionProperty(type=PaletteItem)


class Palette(DataCollection):
    items: CollectionProperty(type=PaletteGroup)
