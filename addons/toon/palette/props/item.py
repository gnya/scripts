from bpy.types import PropertyGroup
from bpy.props import EnumProperty, FloatVectorProperty

from .socket import SocketLinkedItem


class PaletteItem(SocketLinkedItem, PropertyGroup):
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

    def parent_keys(self):
        path = self.path_from_id().rsplit('.', 1)[0]
        group = self.id_data.path_resolve(path)

        return group.items.keys()

    def linked_items(self):
        path = self.path_from_id().rsplit('.', 2)[0]
        palette = self.id_data.path_resolve(path)

        for group in palette.items:
            for item in group.items:
                yield item
