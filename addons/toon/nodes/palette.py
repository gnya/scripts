from toon.utils import override

from bpy.props import StringProperty
from bpy.types import Context, ShaderNodeCustomGroup, UILayout

from toon.palette import ToonPaletteFacade
from toon.props import ToonPaletteSearchIndex
from toon.utils import NodeLinkRebinder


class ToonNodePalette(ShaderNodeCustomGroup):
    bl_idname = 'ToonNodePalette'
    bl_label = 'Palette'

    def _update_property(self, context: Context):
        with NodeLinkRebinder(self):
            self.free()
            self.init(context)

    palette_name: StringProperty(
        name='Palette Name',
        update=_update_property
    )

    group_name: StringProperty(
        name='Group Name',
        update=_update_property
    )

    @override
    def init(self, context: Context):
        palette = ToonPaletteFacade.get(self.palette_name)

        if palette is not None:
            group = palette.get(self.group_name)

            if group is not None:
                self.node_tree = group.node_tree

    @override
    def free(self):
        self.node_tree = None

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
        states = ToonPaletteSearchIndex.current()

        layout.prop_search(
            self, 'palette_name',
            states, 'palettes',
            text='', icon='COLOR'
        )

        state = states.palettes.get(self.palette_name)

        if state is not None:
            layout.prop_search(
                self, 'group_name',
                state, 'groups',
                text='', icon='GROUP'
            )
