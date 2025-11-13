from toon.utils import override

from bpy.props import EnumProperty, FloatVectorProperty
from bpy.types import Context, PropertyGroup

from .base import SocketEntry


class PaletteEntry(SocketEntry, PropertyGroup):
    entry_types = [
        ('COLOR', 'Color', ''),
        ('TEXTURE', 'Texture', ''),
        ('MIX', 'Mix', '')
    ]

    def _update_type(self, context: Context):
        pass

    def _update_color(self, context: Context):
        self.socket().default_value = self.color

    type: EnumProperty(
        items=entry_types, default='COLOR',
        update=_update_type
    )

    color: FloatVectorProperty(
        subtype='COLOR', size=4,
        soft_min=0.0, soft_max=1.0,
        update=_update_color
    )

    @override
    def node_tree(self):
        return self.id_data

    @override
    def linked_entries(self):
        path = self.path_from_id().rsplit('.', 2)[0]
        palette = self.id_data.path_resolve(path)

        for group in palette.entries:
            for entry in group.entries:
                yield entry
