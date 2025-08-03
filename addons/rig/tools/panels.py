import bpy

from rig import utils


UI_CONTENTS = {
    '$view3d.rig_update_asset': {
        '': ('Asset', 'Update', 'FILE_REFRESH', 0, 1.0)
    },
    '$view3d.rig_show_animated_bones': {
        '': ('Pose Mode', 'Animated', 'HIDE_OFF', 100, 0.5)
    },
    '$view3d.rig_show_overrided_bones': {
        '': ('Pose Mode', 'Overrided', 'HIDE_OFF', 101, 0.5)
    },
    '$view3d.rig_copy_pose': {
        '': ('Pose Mode', 'Copy', 'COPYDOWN', 102, 0.5)
    },
    '$view3d.rig_paste_pose': {
        '': ('Pose Mode', 'Paste', 'PASTEDOWN', 103, 0.5)
    },
    '$view3d.rig_show_prefix_bones': {
        'type': ('Edit Mode', 'Prefix', 'HIDE_OFF', 200, 1.0)
    }
}


class VIEW3D_PT_rig_tools(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_tools'
    bl_label = 'Tools'
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
