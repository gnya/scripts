from toon.utils import override

from bpy.types import Context, Panel, UILayout

from toon.manager import PaletteManager
from toon.ops import VIEW3D_OT_toon_add_palette_entry
from toon.ops import VIEW3D_OT_toon_remove_palette
from toon.ops import VIEW3D_OT_toon_remove_palette_entry
from toon.ops import VIEW3D_OT_toon_move_palette_slot
from toon.props import Palette

from .ul_palette import VIEW3D_UL_toon_palette_entry
from .mt_palette import VIEW3D_MT_toon_palette_add_menu
from .mt_palette import VIEW3D_MT_toon_palette_menu
from .mt_palette import VIEW3D_MT_toon_palette_group_menu


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
        sub_col.operator(
            VIEW3D_OT_toon_add_palette_entry.bl_idname,
            text='', icon='ADD'
        )
        sub_col.operator(
            VIEW3D_OT_toon_remove_palette_entry.bl_idname,
            text='', icon='REMOVE'
        )
        sub_col.separator()
        sub_col.menu(
            VIEW3D_MT_toon_palette_group_menu.bl_idname,
            text='', icon='DOWNARROW_HLT'
        )

        if len(palette.slots) > 1:
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

    def _draw_palette_props(self, layout: UILayout, palette: Palette):
        pointer = palette.active_pointer()

        if pointer is not None and pointer.entry is not None:
            row = layout.row()
            row.prop(pointer.entry, 'type', expand=True)

            col = layout.column()
            col.use_property_split = True
            col.use_property_decorate = False

            if pointer.entry.type == 'COLOR':
                col.prop(pointer.entry, 'color', text='Color')
            elif pointer.entry.type == 'TEXTURE':
                col.template_ID(
                    pointer.entry.node(), 'image',
                    new='image.new', open='image.open'
                )
                col.prop(pointer.entry, 'texture_uv_map', text='UV Map')
            elif pointer.entry.type == 'MIX':
                col.prop(pointer.entry, 'mix_factor', text='Factor', slider=True)
                col.prop_search(
                    pointer.entry, 'mix_source_a',
                    pointer.group, 'entries',
                    text='Source A'
                )
                col.prop_search(
                    pointer.entry, 'mix_source_b',
                    pointer.group, 'entries',
                    text='Source B'
                )

            col.separator()

    def _draw_palette(self, layout: UILayout, palette: Palette):
        col = layout.column(align=True)

        box = col.box()
        self._draw_palette_header(box, palette)

        if palette.show_expanded:
            box = col.box()
            self._draw_palette_list(box, palette)
            self._draw_palette_props(box, palette)

    @override
    def draw(self, context: Context):
        layout = self.layout

        layout.menu(
            VIEW3D_MT_toon_palette_add_menu.bl_idname,
            text='Add Palette'
        )

        manager = PaletteManager.instance()

        for palette in manager.palettes():
            layout.context_pointer_set('palette', palette)
            self._draw_palette(layout, palette)
