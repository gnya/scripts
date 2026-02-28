from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.types import Panel

from toon.ops import (
    VIEW3D_OT_toon_palette_add,
    VIEW3D_OT_toon_palette_add_color,
    VIEW3D_OT_toon_palette_move_item,
    VIEW3D_OT_toon_palette_remove,
    VIEW3D_OT_toon_palette_remove_color,
)
from toon.props import ToonPaletteUIState
from toon.utils import override

from .palette_list import VIEW3D_UL_toon_palette_entry
from .palette_menu import VIEW3D_MT_toon_palette, VIEW3D_MT_toon_palette_group

if TYPE_CHECKING:
    from bpy.types import Context, UILayout

    from toon.props import ToonPaletteUIPaletteState


class VIEW3D_PT_toon_palette(Panel):
    bl_idname = "VIEW3D_PT_toon_palette"
    bl_label = "Palette"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Toon"

    def _draw_palette_header(self, layout: UILayout, state: ToonPaletteUIPaletteState):
        row = layout.row()

        sub_row = row.row(align=True)
        icon = "DOWNARROW_HLT" if state.show_expanded else "RIGHTARROW"
        sub_row.prop(state, "show_expanded", text="", emboss=False, icon=icon)
        sub_row.label(icon="COLOR")

        sub_row = row.row(align=True)
        sub_row.prop(state, "palette_name", text="")
        sub_row.menu(VIEW3D_MT_toon_palette.bl_idname, text="", icon="DOWNARROW_HLT")

        sub_row = row.row(align=True)
        sub_row.operator(
            VIEW3D_OT_toon_palette_remove.bl_idname, text="", emboss=False, icon="X"
        )

    def _draw_palette_list(self, layout: UILayout, state: ToonPaletteUIPaletteState):
        row = layout.row()

        row.template_list(
            VIEW3D_UL_toon_palette_entry.bl_idname,
            state.palette_name,
            state,
            "list_items",
            state,
            "active_index",
            rows=12,
            sort_lock=True,
        )

        col = row.column()
        sub_col = col.column(align=True)
        sub_col.operator(
            VIEW3D_OT_toon_palette_add_color.bl_idname, text="", icon="ADD"
        )
        sub_col.operator(
            VIEW3D_OT_toon_palette_remove_color.bl_idname, text="", icon="REMOVE"
        )
        sub_col.separator()
        sub_col.menu(
            VIEW3D_MT_toon_palette_group.bl_idname, text="", icon="DOWNARROW_HLT"
        )

        if len(state.list_items) > 1:
            sub_col.separator()
            o = sub_col.operator(
                VIEW3D_OT_toon_palette_move_item.bl_idname, text="", icon="TRIA_UP"
            )
            o.direction = "UP"
            o = sub_col.operator(
                VIEW3D_OT_toon_palette_move_item.bl_idname, text="", icon="TRIA_DOWN"
            )
            o.direction = "DOWN"

    def _draw_palette_props(self, layout: UILayout, state: ToonPaletteUIPaletteState):
        item = state.active_item()

        if item is None or item.type == "GROUP":
            return

        row = layout.row()
        row.prop(item, "color_type", text="")

        col = layout.column()
        col.use_property_split = True
        col.use_property_decorate = False

        if item.color_type == "COLOR":
            col.prop(*item.color_ptr, text="Color")
        elif item.color_type == "TEXTURE":
            col.template_ID(*item.texture_ptr, new="image.new", open="image.open")
            col.prop(*item.uv_map_ptr, text="UV Map")
        elif item.color_type == "VECTOR":
            col.prop(*item.color_ptr, text="Vector", slider=True)
        elif item.color_type == "VALUE":
            col.prop(*item.color_ptr, text="Value", slider=True)

        col.separator()

    def _draw_palette(self, layout: UILayout, state: ToonPaletteUIPaletteState):
        col = layout.column(align=True)

        box = col.box()
        self._draw_palette_header(box, state)

        if state.show_expanded:
            box = col.box()
            self._draw_palette_list(box, state)
            self._draw_palette_props(box, state)

    @override
    def draw(self, context: Context):
        layout = self.layout

        layout.operator(VIEW3D_OT_toon_palette_add.bl_idname, text="Add Palette")

        for state in ToonPaletteUIState.current_states():
            layout.context_pointer_set("palette_state", state)
            self._draw_palette(layout, state)
