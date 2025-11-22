from toon.utils import override

from bpy.props import StringProperty
from bpy.types import Context, UILayout

from toon.manager import PaletteManager
from toon.props import Palette
from toon.utils import NodeLinkRebinder

from .base import ToonNode


class PaletteNode(ToonNode):
    bl_name = 'PaletteNode'
    bl_label = 'Palette'

    def _get_palette_name(self) -> str:
        manager = PaletteManager.instance()
        node_tree = self.node_tree

        if node_tree is None:
            return ''

        palette = manager.from_data(node_tree)

        if palette is None:
            return ''

        return palette.name

    def _set_palette_name(self, value: str):
        manager = PaletteManager.instance()
        palette = manager.first(value)

        if palette is None:
            return

        with NodeLinkRebinder(self):
            self.node_tree = palette.id_data
            self.update()

    def _update_palette_group_name(self, context: Context):
        with NodeLinkRebinder(self):
            self.update()

    palette_name: StringProperty(
        name='Palette Name',
        get=_get_palette_name, set=_set_palette_name
    )

    palette_group_name: StringProperty(
        name='Palette Group Name',
        update=_update_palette_group_name
    )

    def palette(self) -> Palette | None:
        manager = PaletteManager.instance()
        node_tree = self.node_tree

        if node_tree is None:
            return None

        return manager.from_data(node_tree)

    @override
    def init(self, context: Context):
        pass  # Doing anything.

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

        group = palette.first(self.palette_group_name)

        if group is None:
            return

        for entry in group.entries:
            self.outputs[entry.socket_id].enabled = True

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
        manager = PaletteManager.instance()
        manager.update_ids()

        layout.prop_search(
            self, 'palette_name',
            manager, 'ids_cache',
            text='', icon='COLOR'
        )

        palette = self.palette()

        if palette is not None:
            layout.prop_search(
                self, 'palette_group_name',
                palette, 'entries',
                text='', icon='GROUP'
            )
