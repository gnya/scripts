import bpy
import copy

from rig import ui_drawer


UI_CONTENTS = {}

# Common
UI_CONTENTS[''] = {
    '$view3d.rig_update_asset': {
        '': ('Asset', 'Update', 'FILE_REFRESH', 0, 1.0)
    },
    '$view3d.rig_show_animated_bones': {
        '': ('Show Bones', 'Animated', 'HIDE_OFF', 100, 0.5)
    },
    '$view3d.rig_show_overrided_bones': {
        '': ('Show Bones', 'Overrided', 'HIDE_OFF', 101, 0.5)
    },
    '$view3d.rig_show_prefix_bones': {
        'type': ('Show Bones', 'Prefix (CTR, DEF, MCH, CSP)', 'HIDE_OFF', 102, 1.0)
    },
    '$view3d.rig_copy_pose': {
        '': ('Pose', 'Copy', 'COPYDOWN', 200, 0.5)
    },
    '$view3d.rig_paste_pose': {
        '': ('Pose', 'Paste', 'PASTEDOWN', 201, 0.5)
    },
    '$view3d.rig_attach_light': {
        '': ('Light', 'Attach', 'LIGHT', 300, 1.0)
    }
}


class VIEW3D_PT_rig_tools(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_tools'
    bl_label = 'Tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'VIEW3D_PT_rig_main'

    def draw(self, context):
        obj = context.active_object
        asset_name = obj.name.split('_')[0]
        props = copy.deepcopy(UI_CONTENTS[''])
        asset_props = copy.deepcopy(UI_CONTENTS.get(asset_name, {}))

        for k, v in asset_props.items():
            if k not in props:
                props[k] = {}

            props[k].update(v)

        contents = {}
        ui_drawer.collect_contents(contents, obj, props)

        col = self.layout.column(align=True)
        ui_drawer.draw_contents(col, contents)
