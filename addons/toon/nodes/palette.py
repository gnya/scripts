from bpy.props import StringProperty
from bpy.types import Context

from toon.palette.props import PaletteUI, PaletteName
from toon.utils import override

from .base import ToonNode


class ToonNodePalette(ToonNode):
    bl_name = 'ToonNodePalette'
    bl_label = 'Palette'

    def _update_palette_name(self, context: Context):
        self.init(context)
        self.update()

    def _update_palette_group_name(self, context: Context):
        self.update()

    palette_name: StringProperty(
        name='Palette Name',
        update=_update_palette_name
    )

    palette_group_name: StringProperty(
        name='Palette Group Name',
        update=_update_palette_group_name
    )

    @override
    def node_tree_name(self):
        palette = PaletteUI.instance(self.palette_name)

        if palette is None:
            return ''

        return palette.id_data.name[1:]

    @override
    def init_toon_node(self, context, node_tree):
        pass  # Doing anything.

    @override
    def free(self):
        pass  # Doing anything.

    @override
    def update(self):
        if not self.outputs:
            return

        for output in self.outputs:
            output.enabled = False

        palette = PaletteUI.instance(self.palette_name)

        if palette is None:
            return

        group = palette.items.get(self.palette_group_name)

        if group is None:
            return

        for item in group.items:
            self.outputs[item.socket_id].enabled = True

    @override
    def draw_buttons(self, context, layout):
        layout.prop_search(
            self, 'palette_name',
            PaletteName.prop_data(), PaletteName.PROP_NAME,
            text='', icon='COLOR'
        )

        palette = PaletteUI.instance(self.palette_name)

        if palette is not None:
            layout.prop_search(
                self, 'palette_group_name',
                palette, 'items',
                text='', icon='GROUP'
            )
