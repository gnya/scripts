from bpy.props import StringProperty
from bpy.types import Context, NodeTree, UILayout

from toon.palette.props import Palette, PaletteUI, PaletteName
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
    def init_toon_node(self, context: Context, node_tree: NodeTree):
        pass  # Doing anything.

    @override
    def free(self):
        pass  # Doing anything.

    def _palette_instance(self):
        palette = getattr(self.node_tree, Palette.PROP_NAME, None)

        if palette is None:
            return PaletteUI.instance(self.palette_name)
        elif palette.name == self.palette_name:
            return palette

    @override
    def update(self):
        if len(self.outputs) == 0:
            return

        for output in self.outputs:
            output.enabled = False

        palette = self._palette_instance()

        if palette is None:
            return

        group = palette.items.get(self.palette_group_name)

        if group is None:
            return

        for item in group.items:
            self.outputs[item.socket_id].enabled = True

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
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
