import bpy
import copy
from rig import ui_utils


class VIEW3D_OT_rig_attach_light(bpy.types.Operator):
    bl_idname = 'view3d.rig_attach_light'
    bl_label = 'Attach Light'
    bl_description = 'Attach a light object'
    bl_options = {'UNDO'}

    def execute(self, context):
        return {'FINISHED'}


UI_CONTENTS = {}

# Common
UI_CONTENTS[''] = {
    '': {
        '["quality"]': ('Quality', 'Quality', '', 0, 1.0),
        '["preview_quality"]': ('Quality', 'Preview Quality', '', 1, 1.0)
    }
}

# PTB
UI_CONTENTS['PTB'] = {
    '': {
        'layers[0]': ('Show/Hide Body', 'Body', '', 200, 1.0)
    }
}

_HUMAN_RIG_PROP_INFO = {
    'data': {
        'layers[0]': ('Show/Hide Body', 'Fingers', '', 200, 1.0),
        'layers[1]': ('Show/Hide Body', 'Arm IK', '', 201, 0.5),
        'layers[2]': ('Show/Hide Body', 'Arm FK', '', 202, 0.5),
        'layers[17]': ('Show/Hide Body', 'Leg IK', '', 203, 0.5),
        'layers[18]': ('Show/Hide Body', 'Leg FK', '', 204, 0.5),
        'layers[16]': ('Show/Hide Body', 'Root & Spine', '', 205, 1.0),
        'layers[5]': ('Show/Hide Bones', 'Eye Target', '', 300, 1.0),
        'layers[4]': ('Show/Hide Bones', 'Eyebrows', '', 301, 0.5),
        'layers[20]': ('Show/Hide Bones', 'Eyes', '', 302, 0.5),
        'layers[21]': ('Show/Hide Bones', 'Lips & Jaw', '', 303, 1.0),
        'layers[22]': ('Show/Hide Bones', 'Tooth & Tongue', '', 304, 1.0),
        'layers[6]': ('Show/Hide Bones', 'Expressions', '', 305, 1.0),
        'layers[7]': ('Show/Hide Bones', 'Lattice', '', 306, 1.0),
        'layers[23]': ('Show/Hide Props', 'Properties', '', 600, 1.0)
    },
    'pose.bones["CTR_properties_expression"]': {
        '["auto_ctrl_switching"]': ('Show/Hide Face', 'Auto Switch (Expression)', '', 400, 1.0),
        '["show_double_eyelid"]': ('Show/Hide Face', 'Double Eyelid', '', 401, 1.0),
        '["show_eyelashes_A"]': ('Show/Hide Face', 'Eyelashes A', '', 402, 1.0),
        '["show_lip_line"]': ('Show/Hide Face', 'Lip Line', '', 403, 1.0),
        '["show_eyelashes_B"]': ('Show/Hide Face', 'Eyelashes B', '', 404, 1.0),
        '["show_sweat.L"]': ('Show/Hide Face', 'Sweat L', '', 405, 0.5),
        '["show_sweat.R"]': ('Show/Hide Face', 'Sweat R', '', 406, 0.5),
        '["show_wrinkles_A"]': ('Show/Hide Face', 'Wrinkles A', '', 407, 0.5),
        '["show_wrinkles_B"]': ('Show/Hide Face', 'Wrinkles B', '', 408, 0.5)
    },
    'pose.bones["CTR_properties_head"]': {
        '["head_hinge"]': ('Head', 'Head Hinge', '', 500, 1.0),
        '["neck_hinge"]': ('Head', 'Neck Hinge', '', 501, 1.0),
        '["sticky_eyesockets"]': ('Head', 'Sticky Eyesockets', '', 502, 1.0),
        '["reduce_perspective"]': ('Head', 'Reduce Perspective', '', 503, 1.0)
    },
    'pose.bones["CTR_lattice_target"].constraints[0]': {
        'target': ('Head', 'Camera', '', 504, 1.0)
    },
    '$view3d.rig_attach_light': {
        '': ('Light', 'Attach Light', 'LIGHT', 100, 1.0)
    }
}

# MCP
UI_CONTENTS['MCP'] = copy.deepcopy(_HUMAN_RIG_PROP_INFO)

# MCL
UI_CONTENTS['MCL'] = copy.deepcopy(_HUMAN_RIG_PROP_INFO)
UI_CONTENTS['MCL'][''] = {
    '["show_gloves"]': ('Show/Hide Clothes', 'Gloves', '', 100, 1.0)
}


class VIEW3D_PT_rig_props(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_show'
    bl_label = 'Properties'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'VIEW3D_PT_rig_main'
    bl_order = 1

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
        ui_utils.collect_contents(contents, obj, props)

        col = self.layout.column(align=True)
        ui_utils.draw_contents(col, contents)
