import copy


RIG_PROP_INFO = {}

# Common
RIG_PROP_INFO[''] = {
    '': {
        '["quality"]': ('Quality', 'Quality', 0, 1.0),
        '["preview_quality"]': ('Quality', 'Preview Quality', 1, 1.0)
    }
}

# PTB
RIG_PROP_INFO['PTB'] = {
    '': {
        'layers[0]': ('Show/Hide Body', 'Body', 200, 1.0)
    }
}

_HUMAN_RIG_PROP_INFO = {
    '': {
        'layers[0]': ('Show/Hide Body', 'Fingers', 200, 1.0),
        'layers[1]': ('Show/Hide Body', 'Arm IK', 201, 0.5),
        'layers[2]': ('Show/Hide Body', 'Arm FK', 202, 0.5),
        'layers[17]': ('Show/Hide Body', 'Leg IK', 203, 0.5),
        'layers[18]': ('Show/Hide Body', 'Lef FK', 204, 0.5),
        'layers[16]': ('Show/Hide Body', 'Root & Spine', 205, 1.0),
        'layers[5]': ('Show/Hide Bones', 'Eye Target', 300, 1.0),
        'layers[4]': ('Show/Hide Bones', 'Eyebrows', 301, 0.5),
        'layers[20]': ('Show/Hide Bones', 'Eyes', 302, 0.5),
        'layers[21]': ('Show/Hide Bones', 'Lips & Jaw', 303, 1.0),
        'layers[22]': ('Show/Hide Bones', 'Tooth & Tongue', 304, 1.0),
        'layers[6]': ('Show/Hide Bones', 'Expressions', 305, 1.0),
        'layers[7]': ('Show/Hide Bones', 'Lattice', 306, 1.0),
        'layers[23]': ('Show/Hide Props', 'Properties', 600, 1.0)
    },
    'CTR_properties_expression': {
        '["auto_ctrl_switching"]': ('Show/Hide Face', 'Auto Switch (Expression)', 400, 1.0),
        '["show_double_eyelid"]': ('Show/Hide Face', 'Double Eyelid', 401, 1.0),
        '["show_eyelashes_A"]': ('Show/Hide Face', 'Eyelashes A', 402, 1.0),
        '["show_lip_line"]': ('Show/Hide Face', 'Lip Line', 403, 1.0),
        '["show_eyelashes_B"]': ('Show/Hide Face', 'Eyelashes B', 404, 1.0),
        '["show_sweat.L"]': ('Show/Hide Face', 'Sweat L', 405, 0.5),
        '["show_sweat.R"]': ('Show/Hide Face', 'Sweat R', 406, 0.5),
        '["show_wrinkles_A"]': ('Show/Hide Face', 'Wrinkles A', 407, 0.5),
        '["show_wrinkles_B"]': ('Show/Hide Face', 'Wrinkles B', 408, 0.5)
    },
    'CTR_properties_head': {
        '["head_hinge"]': ('Head', 'Head Hinge', 500, 1.0),
        '["neck_hinge"]': ('Head', 'Neck Hinge', 501, 1.0),
        '["sticky_eyesockets"]': ('Head', 'Sticky Eyesockets', 502, 1.0),
        '["reduce_perspective"]': ('Head', 'Reduce Perspective', 503, 1.0)
    },
    'CTR_lattice_target': {
        'target': ('Head', 'Camera', 504, 1.0)
    }
}

# MCP
RIG_PROP_INFO['MCP'] = copy.deepcopy(_HUMAN_RIG_PROP_INFO)

# MCL
RIG_PROP_INFO['MCL'] = copy.deepcopy(_HUMAN_RIG_PROP_INFO)
RIG_PROP_INFO['MCL'][''].update({
    '["show_gloves"]': ('Show/Hide Clothes', 'Gloves', 100, 1.0)
})
