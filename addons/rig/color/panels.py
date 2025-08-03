import bpy

from rig import utils


UI_CONTENTS = {
    '$view3d.rig_attach_light': {
        '': ('Light', 'Attach', 'LIGHT', 0, 1.0)
    }
}


class VIEW3D_PT_rig_color(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_color'
    bl_label = 'Color'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rig'

    @classmethod
    def poll(cls, context):
        return utils.is_rig(context.active_object)

    def draw(self, context):
        obj = context.active_object

        contents = {}
        utils.ui.collect_contents(contents, obj, UI_CONTENTS)

        col = self.layout.column(align=True)
        utils.ui.draw_contents(col, contents)
