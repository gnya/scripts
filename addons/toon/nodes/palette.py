import bpy

from bpy.props import StringProperty

from .base import ToonNodeBase


def get_palettes():
    for node_tree in bpy.data.node_groups:
        if node_tree.toon_palette.is_available:
            yield node_tree.toon_palette


def get_palette(name):
    for palette in get_palettes():
        if palette.name == name:
            return palette

    return None


class ToonNodePalette(ToonNodeBase):
    bl_name = 'ToonNodePalette'
    bl_label = 'Palette'

    palette_name: StringProperty(name='Palette Name')

    palette_group_name: StringProperty(name='Palette Group Name')

    def init_toon_node(self, context, node_tree):
        pass

    def draw_buttons(self, context, layout):
        layout.prop_search(
            self, 'palette_group_name',
            get_palette(self.palette_name), 'items',
            text='', icon='COLOR'
        )
