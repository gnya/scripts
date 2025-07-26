import bpy
import copy

from rig import ui_drawer


UI_CONTENTS = {}

# Common
UI_CONTENTS[''] = {
    '': {
        '["quality"]': ('Quality', 'Quality', '', 500, 1.0),
        '["preview_quality"]': ('Quality', 'Preview Quality', '', 501, 1.0)
    },
    '$view3d.rig_update_asset': {
        '': ('Asset', 'Update Asset', 'FILE_REFRESH', 0, 1.0)
    },
    '$view3d.rig_show_animated_bones': {
        '': ('Show', 'Show Animated Bones', 'HIDE_OFF', 100, 1.0)
    },
    '$view3d.rig_show_overrided_bones': {
        '': ('Show', 'Show Overrided Bones', 'HIDE_OFF', 100, 1.0)
    },
    '$view3d.rig_copy_pose': {
        '': ('Pose', 'Copy Pose', 'COPYDOWN', 101, 0.5)
    },
    '$view3d.rig_paste_pose': {
        '': ('Pose', 'Paste Pose', 'PASTEDOWN', 102, 0.5)
    },
    '$view3d.rig_copy_whole_pose': {
        '': ('Pose', 'Copy Whole Pose', 'COPYDOWN', 103, 1.0)
    },
    '$view3d.rig_attach_light': {
        '': ('Light', 'Attach Light', 'LIGHT', 200, 1.0)
    }
}


def _layers_icon(value):
    return 'RADIOBUT_ON' if value else 'RADIOBUT_OFF'


def _visibility_icon(value):
    return 'HIDE_OFF' if value else 'HIDE_ON'


# PTB
UI_CONTENTS['PTB'] = {
    '': {
        'layers[0]': ('Body', 'Body', _layers_icon, 700, 1.0)
    }
}

_HUMAN_RIG_PROP_INFO = {
    'data': {
        'layers[16]': ('Body', 'Root & Spine', _layers_icon, 700, 1.0),
        'layers[1]': ('Body', 'Arm IK', _layers_icon, 701, 0.5),
        'layers[2]': ('Body', 'Arm FK', _layers_icon, 702, 0.5),
        'layers[17]': ('Body', 'Leg IK', _layers_icon, 703, 0.5),
        'layers[18]': ('Body', 'Leg FK', _layers_icon, 704, 0.5),
        'layers[0]': ('Body', 'Fingers', _layers_icon, 705, 1.0),
        'layers[5]': ('Eyes', 'Eye Target', _layers_icon, 800, 1.0),
        'layers[4]': ('Eyes', 'Eyebrows', _layers_icon, 801, 0.5),
        'layers[20]': ('Eyes', 'Eyes', _layers_icon, 802, 0.5),
        'layers[21]': ('Mouth', 'Lips & Jaw', _layers_icon, 900, 1.0),
        'layers[22]': ('Mouth', 'Tooth & Tongue', _layers_icon, 901, 1.0),
        'layers[6]': ('Expressions', 'Expressions', _layers_icon, 1000, 1.0),
        'layers[7]': ('Lattice', 'Lattice', _layers_icon, 1100, 1.0),
        'layers[23]': ('Properties', 'Properties', _layers_icon, 1200, 1.0)
    },
    'pose.bones["CTR_properties_expression"]': {
        '["show_double_eyelid"]': ('Eyes', 'Double Eyelid', _visibility_icon, 803, 1.0),
        '["show_eyelashes_A"]': ('Eyes', 'Eyelashes A', _visibility_icon, 804, 1.0),
        '["show_lip_line"]': ('Mouth', 'Lip Line', _visibility_icon, 902, 1.0),
        '["show_eyelashes_B"]': ('Expressions', 'Eyelashes B', _visibility_icon, 1001, 1.0),
        '["show_sweat.L"]': ('Expressions', 'Sweat L', _visibility_icon, 1002, 0.5),
        '["show_sweat.R"]': ('Expressions', 'Sweat R', _visibility_icon, 1003, 0.5),
        '["show_wrinkles_A"]': ('Expressions', 'Wrinkles A', _visibility_icon, 1004, 0.5),
        '["show_wrinkles_B"]': ('Expressions', 'Wrinkles B', _visibility_icon, 1005, 0.5)
    },
    'pose.bones["CTR_properties_head"]': {
        '["head_hinge"]': ('Body', 'Head Hinge', '', 706, 1.0),
        '["neck_hinge"]': ('Body', 'Neck Hinge', '', 707, 1.0),
        '["sticky_eyesockets"]': ('Eyes', 'Sticky Eyesockets', '', 805, 1.0),
        '["reduce_perspective"]': ('Lattice', 'Reduce Perspective', '', 1101, 1.0)
    },
    'pose.bones["CTR_lattice_target"].constraints[0]': {
        'target': ('Lattice', 'Camera', '', 1102, 1.0)
    }
}

# MCP
UI_CONTENTS['MCP'] = copy.deepcopy(_HUMAN_RIG_PROP_INFO)

# MCL
UI_CONTENTS['MCL'] = copy.deepcopy(_HUMAN_RIG_PROP_INFO)
UI_CONTENTS['MCL'][''] = {
    '["show_gloves"]': ('Clothes', 'Gloves', _visibility_icon, 600, 1.0)
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
        ui_drawer.collect_contents(contents, obj, props)

        col = self.layout.column(align=True)
        ui_drawer.draw_contents(col, contents)
