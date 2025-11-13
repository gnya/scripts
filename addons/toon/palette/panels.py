from typing import Any
from toon.utils import override

from bpy.props import StringProperty
from bpy.types import Context, Menu, Panel, UILayout, UIList

from .ops_add_remove import (
    VIEW3D_OT_toon_add_palette,
    VIEW3D_OT_toon_remove_palette,
    VIEW3D_OT_toon_add_palette_group,
    VIEW3D_OT_toon_remove_palette_group,
    VIEW3D_OT_toon_add_palette_entry,
    VIEW3D_OT_toon_remove_palette_entry
)
from .ops_convert import VIEW3D_OT_toon_convert_palette
from .ops_copy_paste import VIEW3D_OT_toon_copy_palette
from .ops_copy_paste import VIEW3D_OT_toon_paste_palette
from .ops_move import VIEW3D_OT_toon_move_palette
from .ops_move import VIEW3D_OT_toon_move_palette_slot
from .palette import Palette, PalettePointer, PaletteSlot, PaletteManager


class VIEW3D_UL_toon_palette_entry(UIList):
    bl_idname = 'VIEW3D_UL_toon_palette_entry'

    filter_name: StringProperty(
        default='', options={'TEXTEDIT_UPDATE'}
    )

    @override
    def draw_item(
            self, context: Context, layout: UILayout, data: Palette | None,
            item: PaletteSlot | None, icon: int | None, active_data: Any,
            active_property: str | None, index: int | None = 0, flt_flag: int | None = 0
    ):
        if data is None or item is None:
            return

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            p = data.get_pointer(item)
            row = layout.row(align=True)

            if p is None:
                return
            elif p.entry is None:
                i = 'DOWNARROW_HLT' if p.group.show_expanded else 'RIGHTARROW'
                row.prop(p.group, 'show_expanded', text='', emboss=False, icon=i)
                row.prop(p.group, 'name', text='', emboss=False)
            else:
                row.separator(factor=3.0)
                row.prop(p.entry, 'color', text='')
                row.prop(p.entry, 'name', text='', emboss=False)
        elif self.layout_type in {'GRID'}:
            pass

    def _filter_name(self, name: str, filter_name: str):
        if not self.use_filter_invert:
            return filter_name.lower() in name.lower()
        else:
            return filter_name.lower() not in name.lower()

    def _filter_item(self, p: PalettePointer | None) -> bool:
        if p is None:
            return False
        elif p.entry is not None:
            if not self.filter_name:
                return p.group.show_expanded

            if self._filter_name(p.entry.name, self.filter_name):
                return p.group.show_expanded
        else:
            if not self.filter_name:
                return True

            if self._filter_name(p.group.name, self.filter_name):
                return True

            for child in p.group.entries:
                if self._filter_name(child.name, self.filter_name):
                    return True

        return False

    @override
    def filter_items(
            self, context: Context, data: Palette | None, property: str
    ) -> tuple[list[int], list[int]]:
        if data is None:
            return [], []

        slots = getattr(data, property)
        filter_flags = [self.bitflag_filter_item] * len(slots)

        for i, slot in enumerate(slots):
            flag = self._filter_item(data.get_pointer(slot))

            if not (flag ^ self.use_filter_invert):
                filter_flags[i] = ~self.bitflag_filter_item

        return filter_flags, []


class VIEW3D_MT_toon_palette_menu(Menu):
    bl_idname = 'VIEW3D_MT_toon_palette_menu'
    bl_label = 'Palette Specials'

    @override
    def draw(self, context: Context):
        layout = self.layout

        layout.operator(
            VIEW3D_OT_toon_copy_palette.bl_idname,
            text='Copy Palette', icon='COPYDOWN'
        )
        layout.operator(
            VIEW3D_OT_toon_paste_palette.bl_idname,
            text='Paste Palette', icon='PASTEDOWN'
        )
        layout.separator()
        o = layout.operator(
            VIEW3D_OT_toon_move_palette.bl_idname,
            text='Move Palette', icon='TRIA_UP'
        )
        o.direction = 'UP'
        o = layout.operator(
            VIEW3D_OT_toon_move_palette.bl_idname,
            text='Move Palette', icon='TRIA_DOWN'
        )
        o.direction = 'DOWN'


class VIEW3D_PT_toon_palette(Panel):
    bl_idname = 'VIEW3D_PT_toon_palette'
    bl_label = 'Palette'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Toon'

    def _draw_palette_list(self, layout: UILayout, palette: Palette):
        row = layout.row()

        row.template_list(
            VIEW3D_UL_toon_palette_entry.bl_idname,
            palette.name,
            palette, 'slots', palette, 'active_slot_id',
            rows=12, sort_lock=True
        )

        col = row.column()
        sub_col = col.column(align=True)
        sub_col.label(icon='GROUP')
        sub_col.operator(
            VIEW3D_OT_toon_add_palette_group.bl_idname,
            text='', icon='ADD'
        )
        sub_col.operator(
            VIEW3D_OT_toon_remove_palette_group.bl_idname,
            text='', icon='REMOVE'
        )
        sub_col.separator()
        sub_col.label(icon='COLOR')
        sub_col.operator(
            VIEW3D_OT_toon_add_palette_entry.bl_idname,
            text='', icon='ADD'
        )
        sub_col.operator(
            VIEW3D_OT_toon_remove_palette_entry.bl_idname,
            text='', icon='REMOVE'
        )
        sub_col.separator()
        o = sub_col.operator(
            VIEW3D_OT_toon_move_palette_slot.bl_idname,
            text='', icon='TRIA_UP'
        )
        o.direction = 'UP'
        o = sub_col.operator(
            VIEW3D_OT_toon_move_palette_slot.bl_idname,
            text='', icon='TRIA_DOWN'
        )
        o.direction = 'DOWN'

    def _draw_palette_header(self, layout: UILayout, palette: Palette):
        row = layout.row()

        sub_row = row.row(align=True)
        icon = 'DOWNARROW_HLT' if palette.show_expanded else 'RIGHTARROW'
        sub_row.prop(palette, 'show_expanded', text='', emboss=False, icon=icon)
        sub_row.label(icon='COLOR')

        sub_row = row.row(align=True)
        sub_row.prop(palette, 'name', text='')
        sub_row.menu(
            VIEW3D_MT_toon_palette_menu.bl_idname,
            text='', icon='DOWNARROW_HLT'
        )

        sub_row = row.row(align=True)
        sub_row.operator(
            VIEW3D_OT_toon_remove_palette.bl_idname,
            text='', emboss=False, icon='X'
        )

    def _draw_palette(self, layout: UILayout, palette: Palette):
        col = layout.column(align=True)

        box = col.box()
        self._draw_palette_header(box, palette)

        if palette.show_expanded:
            box = col.box()
            self._draw_palette_list(box, palette)

    @override
    def draw(self, context: Context):
        layout = self.layout

        row = layout.row(align=True)
        row.operator(
            VIEW3D_OT_toon_add_palette.bl_idname,
            text='Add Palette', icon='ADD'
        )
        row.operator(
            VIEW3D_OT_toon_convert_palette.bl_idname,
            text='', icon='NODETREE'
        )

        manager = PaletteManager.instance()

        for palette in manager.palettes():
            layout.context_pointer_set('palette', palette)
            self._draw_palette(layout, palette)
