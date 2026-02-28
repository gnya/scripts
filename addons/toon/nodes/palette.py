from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.props import StringProperty
from bpy.types import ShaderNodeCustomGroup

from toon.palette import get_group_name, get_node_tree, get_palette_name
from toon.props import ToonPaletteSearchIndex
from toon.utils import NodeLinkRebinder, override

if TYPE_CHECKING:
    from bpy.types import Context, UILayout


class ToonNodePalette(ShaderNodeCustomGroup):
    bl_idname = "ToonNodePalette"
    bl_label = "Palette"

    def _get_palette_name(self) -> str:
        return get_palette_name(self.node_tree)

    def _set_palette_name(self, value: str):
        with NodeLinkRebinder(self):
            self.node_tree = get_node_tree(value)

    palette_name: StringProperty(
        name="Palette Name", get=_get_palette_name, set=_set_palette_name
    )

    def _get_group_name(self) -> str:
        return get_group_name(self.node_tree)

    def _set_group_name(self, value: str):
        with NodeLinkRebinder(self):
            self.node_tree = get_node_tree(self.palette_name, value)

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
