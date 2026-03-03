from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.props import StringProperty
from bpy.types import ShaderNodeCustomGroup

from toon.palette import (
    get_group_name_full,
    get_node_tree,
    get_palette_name,
    get_palette_name_full,
    parse_name_full,
)
from toon.props import ToonPaletteSearchIndex
from toon.utils import NodeLinkRebinder, override

if TYPE_CHECKING:
    from bpy.types import Context, UILayout


class ToonNodePalette(ShaderNodeCustomGroup):
    bl_idname = "ToonNodePalette"
    bl_label = "Palette"

    def _get_palette_name_full(self) -> str:
        return get_palette_name_full(self.node_tree)

    def _set_palette_name_full(self, value: str):
        with NodeLinkRebinder(self):
            name, library = parse_name_full(value)
            self.node_tree = get_node_tree(name, library=library)

    palette_name_full: StringProperty(
        name="Palette Name Full", get=_get_palette_name_full, set=_set_palette_name_full
    )

    def _get_group_name_full(self) -> str:
        return get_group_name_full(self.node_tree)

    def _set_group_name_full(self, value: str):
        with NodeLinkRebinder(self):
            name, library = parse_name_full(value)
            palette_name = get_palette_name(self.node_tree)
            self.node_tree = get_node_tree(palette_name, name, library)

    group_name_full: StringProperty(
        name="Group Name Full", get=_get_group_name_full, set=_set_group_name_full
    )

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
        states = ToonPaletteSearchIndex.current()

        layout.prop_search(
            self, "palette_name_full", states, "palettes", text="", icon="COLOR"
        )

        state = states.palettes.get(self.palette_name_full)

        if state is not None:
            layout.prop_search(
                self, "group_name_full", state, "groups", text="", icon="GROUP"
            )
        elif len(states.orphans) > 0:
            layout.prop_search(
                self, "group_name_full", states, "orphans", text="", icon="GROUP"
            )
