from toon.utils import override

from bpy.props import StringProperty
from bpy.types import Context, ShaderNodeCustomGroup, UILayout

from toon.props import ToonPaletteFacade
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
        facade = ToonPaletteFacade.instance()
        facade.update()

        self.node_tree = facade.get_node_tree(self.palette_name, self.group_name)

    @override
    def free(self):
        self.node_tree = None

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
        facade = ToonPaletteFacade.instance()
        facade.update()

        layout.prop_search(
            self, 'palette_name',
            facade, 'palettes',
            text='', icon='COLOR'
        )

        index = facade.palettes.find(self.palette_name)

        if index >= 0:
            palette = facade.palettes[index]
            layout.prop_search(
                self, 'group_name',
                palette, 'groups',
                text='', icon='GROUP'
            )
