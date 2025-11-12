from bpy.props import StringProperty
from bpy.types import Context, Panel, UILayout, UIList
from typing import Any

from .palette import PalettePointer, PaletteSlot, PaletteUI
from .ops import (
    VIEW3D_OT_toon_add_palette,
    VIEW3D_OT_toon_remove_palette,
    VIEW3D_OT_toon_add_palette_group,
    VIEW3D_OT_toon_remove_palette_group,
    VIEW3D_OT_toon_add_palette_item,
    VIEW3D_OT_toon_remove_palette_item,
    VIEW3D_OT_toon_move_palette_slot
)


class VIEW3D_UL_toon_palette_item(UIList):
    filter_name: StringProperty(
        default='', options={'TEXTEDIT_UPDATE'}
    )

    def draw_item(
            self, context: Context, layout: UILayout, data: PaletteUI | None,
            item: PaletteSlot | None, icon: int | None, active_data: Any,
            active_property: str | None, index: int | None = 0, flt_flag: int | None = 0
    ):
        if data is None or item is None:
            return

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            p = data.get_item(item)
            row = layout.row(align=True)

            if p is None:
                return
            elif p.item is None:
                i = 'DOWNARROW_HLT' if p.group.show_expanded else 'RIGHTARROW'
                row.prop(p.group, 'show_expanded', text='', emboss=False, icon=i)
                row.prop(p.group, 'name', text='', emboss=False)
            else:
                row.separator(factor=3.0)
                row.prop(p.item, 'color', text='')
                row.prop(p.item, 'name', text='', emboss=False)
        elif self.layout_type in {'GRID'}:
            pass

    def _filter_item_name(self, name: str, filter_name: str):
        if not self.use_filter_invert:
            return filter_name.lower() in name.lower()
        else:
            return filter_name.lower() not in name.lower()

    def _filter_item(self, p: PalettePointer | None) -> bool:
        if p is None:
            return False
        elif p.item is not None:
            if not self.filter_name:
                return p.group.show_expanded

            if self._filter_item_name(p.item.name, self.filter_name):
                return p.group.show_expanded
        else:
            if not self.filter_name:
                return True

            if self._filter_item_name(p.group.name, self.filter_name):
                return True

            for child in p.group.items:
                if self._filter_item_name(child.name, self.filter_name):
                    return True

        return False

    def filter_items(
            self, context: Context, data: PaletteUI | None, property: str
    ) -> tuple[list[int], list[int]]:
        if data is None:
            return [], []

        slots = getattr(data, property)
        filter_flags = [self.bitflag_filter_item] * len(slots)

        for i, slot in enumerate(slots):
            flag = self._filter_item(data.get_item(slot))

            if not (flag ^ self.use_filter_invert):
                filter_flags[i] = ~self.bitflag_filter_item

        return filter_flags, []


class VIEW3D_PT_toon_palette(Panel):
    bl_label = 'Palette'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Toon'

    def draw_palette_list(self, layout: UILayout, palette: PaletteUI):
        row = layout.row()

        row.template_list(
            'VIEW3D_UL_toon_palette_item', palette.name,
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
            VIEW3D_OT_toon_add_palette_item.bl_idname,
            text='', icon='ADD'
        )
        sub_col.operator(
            VIEW3D_OT_toon_remove_palette_item.bl_idname,
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

    def draw_palette_header(self, layout: UILayout, palette: PaletteUI):
        row = layout.row(align=True)

        icon = 'DOWNARROW_HLT' if palette.show_expanded else 'RIGHTARROW'
        row.prop(palette, 'show_expanded', text='', emboss=False, icon=icon)
        row.label(icon='COLOR')
        row.prop(palette, 'name', text='')
        row.operator(
            VIEW3D_OT_toon_remove_palette.bl_idname,
            text='', emboss=False, icon='X'
        )

    def draw_palette(self, layout: UILayout, palette: PaletteUI):
        col = layout.column(align=True)

        box = col.box()
        self.draw_palette_header(box, palette)

        if palette.show_expanded:
            box = col.box()
            self.draw_palette_list(box, palette)

    def draw(self, context: Context):
        layout = self.layout

        layout.operator(
            VIEW3D_OT_toon_add_palette.bl_idname,
            text='Add Palette', icon='ADD'
        )

        for palette in PaletteUI.instances():
            layout.context_pointer_set('palette', palette)
            self.draw_palette(layout, palette)
