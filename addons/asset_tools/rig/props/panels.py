import bpy
import copy

from asset_tools import utils


def _layers_icon(value):
    return 'RADIOBUT_ON' if value else 'RADIOBUT_OFF'


def _visibility_icon(value):
    return 'HIDE_OFF' if value else 'HIDE_ON'


UI_CONTENTS = {}

# Common
UI_CONTENTS[''] = {
    'Quality': {
        '["quality"]': ('Quality', '', 0, 1.0),
        '["preview_quality"]': ('Preview Quality', '', 1, 1.0)
    }
}

# PTB
UI_CONTENTS['PTB'] = {
    'Body': {
        'data.layers[0]': ('Body', _layers_icon, 0, 1.0)
    }
}

_HUMAN_UI_CONTENTS = {
    'Body': {
        'data': {
            'layers[16]': ('Root & Spine', _layers_icon, 0, 1.0),
            'layers[1]': ('Arm IK', _layers_icon, 1, 0.5),
            'layers[2]': ('Arm FK', _layers_icon, 2, 0.5),
            'layers[17]': ('Leg IK', _layers_icon, 3, 0.5),
            'layers[18]': ('Leg FK', _layers_icon, 4, 0.5),
            'layers[0]': ('Fingers', _layers_icon, 5, 1.0)
        },
        'pose.bones["CTR_properties_head"]': {
            '["head_hinge"]': ('Head Hinge', '', 6, 1.0),
            '["neck_hinge"]': ('Neck Hinge', '', 7, 1.0)
        }
    },
    'Eyes': {
        'data': {
            'layers[5]': ('Eye Target', _layers_icon, 0, 1.0),
            'layers[4]': ('Eyebrows', _layers_icon, 1, 0.5),
            'layers[20]': ('Eyes', _layers_icon, 2, 0.5)
        },
        'pose.bones["CTR_properties_expression"]': {
            '["show_double_eyelid"]': ('Double Eyelid', _visibility_icon, 3, 1.0),
            '["show_eyelashes_A"]': ('Eyelashes A', _visibility_icon, 4, 1.0)
        },
        'pose.bones["CTR_properties_head"]': {
            '["sticky_eyesockets"]': ('Sticky Eyesockets', '', 5, 1.0)
        }
    },
    'Mouth': {
        'data': {
            'layers[21]': ('Lips & Jaw', _layers_icon, 0, 1.0),
            'layers[22]': ('Tooth & Tongue', _layers_icon, 1, 1.0)
        },
        'pose.bones["CTR_properties_expression"]': {
            '["show_lip_line"]': ('Lip Line', _visibility_icon, 2, 1.0)
        }
    },
    'Expressions': {
        'data.layers[6]': ('Expressions', _layers_icon, 0, 1.0),
        'pose.bones["CTR_properties_expression"]': {
            '["show_eyelashes_B"]': ('Eyelashes B', _visibility_icon, 1, 1.0),
            '["show_sweat.L"]': ('Sweat L', _visibility_icon, 2, 0.5),
            '["show_sweat.R"]': ('Sweat R', _visibility_icon, 3, 0.5),
            '["show_wrinkles_A"]': ('Wrinkles A', _visibility_icon, 4, 0.5),
            '["show_wrinkles_B"]': ('Wrinkles B', _visibility_icon, 5, 0.5)
        },
    },
    'Lattice': {
        'data.layers[7]': ('Lattice', _layers_icon, 0, 1.0),
        'pose.bones["CTR_properties_head"]': {
            '["reduce_perspective"]': ('Reduce Perspective', '', 1, 1.0)
        }
    },
    'Properties': {
        'data.layers[23]': ('Properties', _layers_icon, 0, 1.0)
    }
}

# MCP
UI_CONTENTS['MCP'] = copy.deepcopy(_HUMAN_UI_CONTENTS)

# MCL
UI_CONTENTS['MCL'] = copy.deepcopy(_HUMAN_UI_CONTENTS)
UI_CONTENTS['MCL'][''] = {
    'Clothes': {
        '["show_gloves"]': ('Gloves', _visibility_icon, 0, 1.0)
    }
}


class VIEW3D_PT_rig_props(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_props'
    bl_label = 'Properties'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rig'
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return utils.is_rig(context.active_object)

    def draw(self, context):
        obj = context.active_object
        name = obj.name.split('_')[0]
        contents = (UI_CONTENTS[''], UI_CONTENTS.get(name, {}))
        col = self.layout.column(align=True)

        utils.ui.draw(col, contents, obj)
