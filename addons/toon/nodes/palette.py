from bpy.props import StringProperty

from toon.palette.props import PaletteUI, PaletteName

from .base import ToonNodeBase


class ToonNodePalette(ToonNodeBase):
    bl_name = 'ToonNodePalette'
    bl_label = 'Palette'

    palette_name: StringProperty(name='Palette Name')

    palette_group_name: StringProperty(name='Palette Group Name')

    def _get_palette(self):
        for palette in PaletteUI.instances():
            if palette.name == self.palette_name:
                return palette

        return None

    def init_toon_node(self, context, node_tree):
        pass

    def draw_buttons(self, context, layout):
        layout.prop_search(
            self, 'palette_name',
            PaletteName.prop_data(), PaletteName.PROP_NAME,
            text='', icon='COLOR'
        )

        palette = self._get_palette()

        if palette is not None:
            layout.prop_search(
                self, 'palette_group_name',
                palette, 'items',
                text='', icon='GROUP'
            )
