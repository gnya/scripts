from bpy.props import StringProperty
from bpy.types import Context, ShaderNodeCustomGroup, UILayout

from toon.palette import (
    ToonPalette,
    ToonPaletteFacade,
    get_group_name,
    get_palette_name,
)
from toon.props import ToonPaletteSearchIndex
from toon.utils import NodeLinkRebinder, override


class ToonNodePalette(ShaderNodeCustomGroup):
    bl_idname = "ToonNodePalette"
    bl_label = "Palette"

    def _get_palette_name(self) -> str:
        if self.node_tree is None:
            return ""

        return get_palette_name(self.node_tree)

    def _set_palette_name(self, value: str):
        with NodeLinkRebinder(self):
            if (palette := ToonPaletteFacade.get(value)) is None:
                self.node_tree = None
            else:
                self.node_tree = palette.header

    palette_name: StringProperty(
        name="Palette Name", get=_get_palette_name, set=_set_palette_name
    )

    def _get_group_name(self) -> str:
        if self.node_tree is None:
            return ""

        return get_group_name(self.node_tree)

    def _set_group_name(self, value: str):
        if self.node_tree is None:
            return

        palette = ToonPalette.from_node_tree(self.node_tree)

        if palette is None:
            return

        with NodeLinkRebinder(self):
            if (group := palette.get(value)) is None:
                self.node_tree = palette.header
            else:
                self.node_tree = group.node_tree

    group_name: StringProperty(
        name="Group Name", get=_get_group_name, set=_set_group_name
    )

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
        states = ToonPaletteSearchIndex.current()

        layout.prop_search(
            self, "palette_name", states, "palettes", text="", icon="COLOR"
        )

        state = states.palettes.get(self.palette_name)

        if state is not None:
            layout.prop_search(
                self, "group_name", state, "groups", text="", icon="GROUP"
            )
