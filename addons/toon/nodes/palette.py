from toon.utils import override

from bpy.props import StringProperty
from bpy.types import Context, UILayout

from toon.palette.palette import Palette, PaletteManager

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

    def palette(self) -> Palette | None:
        manager = PaletteManager.instance()
        palette = manager.get_entry(self.node_tree)

        if palette is None or palette.name != self.palette_name:
            palette = manager.get_entry(self.palette_name)

        return palette

    @override
    def node_tree_name(self) -> str:
        palette = self.palette()

        if palette is None:
            return ''

        return palette.id_data.name[1:]

    @override
    def free(self):
        pass  # Doing anything.

    @override
    def update(self):
        if len(self.outputs) == 0:
            return

        for o in self.outputs:
            o.enabled = False

        palette = self.palette()

        if palette is None:
            return

        group = palette.entries.get(self.palette_group_name)

        if group is None:
            return

        for entry in group.entries:
            self.outputs[entry.socket_id].enabled = True

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
        manager = PaletteManager.instance()

        layout.prop_search(
            self, 'palette_name',
            manager, 'entries',
            text='', icon='COLOR'
        )

        palette = self.palette()

        if palette is not None:
            layout.prop_search(
                self, 'palette_group_name',
                palette, 'entries',
                text='', icon='GROUP'
            )
