import bpy

from asset_tools import utils


UI_CONTENTS = {
    'Asset': {
        '$view3d.rig_update_asset': ('Update', 'FILE_REFRESH', 0, 1.0)
    },
    'Pose Mode': {
        '$view3d.rig_show_animated_bones': {
            '': ('Animated', 'HIDE_OFF', 100, 0.5)
        },
        '$view3d.rig_show_overrided_bones': {
            '': ('Overrided', 'HIDE_OFF', 101, 0.5)
        },
        '$view3d.rig_copy_pose': {
            '': ('Copy', 'COPYDOWN', 102, 0.5)
        },
        '$view3d.rig_paste_pose': {
            '': ('Paste', 'PASTEDOWN', 103, 0.5)
        }
    },
    'Edit Mode': {
        '$view3d.rig_show_prefix_bones': {
            'type': ('Prefix', 'HIDE_OFF', 200, 1.0)
        }
    }
}


class VIEW3D_PT_rig_tools(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_tools'
    bl_label = 'Tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rig'
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return utils.is_rig(context.active_object)

    def draw(self, context):
        obj = context.active_object
        col = self.layout.column(align=True)

        utils.ui.draw(col, UI_CONTENTS, obj)
