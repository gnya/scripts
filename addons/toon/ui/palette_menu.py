from toon.utils import override

from bpy.types import Context, Menu

from toon.ops import VIEW3D_OT_toon_palette_add_group
from toon.ops import VIEW3D_OT_toon_palette_remove_group


class VIEW3D_MT_toon_palette_group(Menu):
    bl_idname = 'VIEW3D_MT_toon_palette_group_menu'
    bl_label = 'Group Specials'

    @override
    def draw(self, context: Context):
        layout = self.layout

        layout.operator(
            VIEW3D_OT_toon_palette_add_group.bl_idname,
            text='Add Group', icon='ADD'
        )
        layout.operator(
            VIEW3D_OT_toon_palette_remove_group.bl_idname,
            text='Remove Group', icon='REMOVE'
        )
