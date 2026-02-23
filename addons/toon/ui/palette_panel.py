from toon.utils import override

from bpy.types import Context, Panel

from toon.ops import VIEW3D_OT_toon_palette_add


class VIEW3D_PT_toon_palette(Panel):
    bl_idname = 'VIEW3D_PT_toon_palette'
    bl_label = 'Palette'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Toon'

    @override
    def draw(self, context: Context):
        layout = self.layout

        layout.operator(
            VIEW3D_OT_toon_palette_add.bl_idname,
            text='Add Palette'
        )
