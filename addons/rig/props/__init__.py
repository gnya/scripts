import bpy
import copy
import json
import mathutils
import re
from rig import ui_utils


class VIEW3D_OT_rig_attach_light(bpy.types.Operator):
    bl_idname = 'view3d.rig_attach_light'
    bl_label = 'Attach Light'
    bl_description = 'Attach a light object'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return False

    def execute(self, context):
        return {'FINISHED'}


class VIEW3D_OT_rig_copy_pose(bpy.types.Operator):
    bl_idname = 'view3d.rig_copy_pose'
    bl_label = 'Copy Pose (World Space)'
    bl_description = 'Copy pose (world space)'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if not obj or not obj.type == 'ARMATURE':
            return False

        if context.mode != 'POSE':
            return False

        return True

    def execute(self, context):
        obj = context.active_object
        bones = obj.pose.bones

        data = {}

        for b in bones:
            if not re.match('CTR_.*', b.name):
                continue

            if not b.bone.select:
                continue

            m = obj.convert_space(
                pose_bone=b, matrix=b.matrix,
                from_space='POSE', to_space='WORLD'
            )

            data[b.name] = {
                'space': 'WORLD',
                'matrix': [list(r) for r in m.row]
            }

        context.window_manager.clipboard = json.dumps(data)

        return {'FINISHED'}


def _calc_depth(deps, bone_depth):
    if len(deps) == 0:
        return 0

    max_depth = 0

    for dep in deps:
        if dep not in bone_depth:
            return -1
        else:
            if max_depth < bone_depth[dep]:
                max_depth = bone_depth[dep]

    return max_depth + 1


# ref: formatter/rules/utils/bone_utils.py
def _bones_used_in_constraint(constraint, armature):
    used_bones = set()

    if constraint.owner_space == 'CUSTOM' or constraint.target_space == 'CUSTOM':
        if constraint.space_object == armature and constraint.space_subtarget:
            used_bones.add(constraint.space_subtarget)

    match constraint.type:
        case 'ARMATURE':
            for t in constraint.targets:
                if t.target == armature and t.subtarget:
                    used_bones.add(t.subtarget)
        case 'COPY_LOCATION':
            if constraint.target == armature and constraint.subtarget:
                used_bones.add(constraint.subtarget)
        case 'COPY_ROTATION':
            if constraint.target == armature and constraint.subtarget:
                used_bones.add(constraint.subtarget)
        case 'COPY_SCALE':
            if constraint.target == armature and constraint.subtarget:
                used_bones.add(constraint.subtarget)
        case 'COPY_TRANSFORMS':
            if constraint.target == armature and constraint.subtarget:
                used_bones.add(constraint.subtarget)
        case 'DAMPED_TRACK':
            if constraint.target == armature and constraint.subtarget:
                used_bones.add(constraint.subtarget)
        case 'IK':
            if constraint.pole_target == armature and constraint.pole_subtarget:
                used_bones.add(constraint.pole_subtarget)

            if constraint.target == armature and constraint.subtarget:
                used_bones.add(constraint.subtarget)
        case 'LOCKED_TRACK':
            if constraint.target == armature and constraint.subtarget:
                used_bones.add(constraint.subtarget)
        case 'LIMIT_DISTANCE':
            if constraint.target == armature and constraint.subtarget:
                used_bones.add(constraint.subtarget)
        case 'LIMIT_LOCATION':
            pass
        case 'LIMIT_SCALE':
            pass
        case 'LIMIT_ROTATION':
            pass
        case 'PIVOT':
            if constraint.target == armature and constraint.subtarget:
                used_bones.add(constraint.subtarget)
        case 'SHRINKWRAP':
            pass
        case 'STRETCH_TO':
            if constraint.target == armature and constraint.subtarget:
                used_bones.add(constraint.subtarget)
        case 'TRACK_TO':
            if constraint.target == armature and constraint.subtarget:
                used_bones.add(constraint.subtarget)
        case 'TRANSFORM':
            if constraint.target == armature and constraint.subtarget:
                used_bones.add(constraint.subtarget)

    return used_bones


# ref: formatter/rules/utils/bone_utils.py (only check "PoseBone")
def _bones_used_in_driver(driver, armature):
    used_bones = set()

    for v in driver.driver.variables:
        for t in v.targets:
            if t.id != armature:
                continue

            if t.bone_target:
                used_bones.add(t.bone_target)

            m = re.search(r'pose.bones\["([^"]+)"\]', t.data_path)

            if m:
                used_bones.add(m.group(1))

    return used_bones


def _dependence_depth(armature):
    # Enumerate other bones on which the bone depends.
    bones = armature.pose.bones
    deps = {}

    for b in bones:
        deps[b.name] = set()

        if b.parent:
            deps[b.name].add(b.parent.name)

        for c in b.constraints:
            deps[b.name] |= _bones_used_in_constraint(c, armature)

    if armature.animation_data:
        for d in armature.animation_data.drivers:
            if m := re.search(r'pose.bones\["([^"]+)"\]', d.data_path):
                deps[m.group(1)] |= _bones_used_in_driver(d, armature)

    # Calculate the depth of dependence of the bone.
    bone_depth = {}
    last_length = len(deps)

    while deps:
        bone_names = list(deps.keys())

        for bone in bone_names:
            depth = _calc_depth(deps[bone], bone_depth)

            if depth >= 0:
                bone_depth[bone] = depth
                deps.pop(bone)

        if last_length == len(deps):
            break

        last_length = len(deps)

    # For cyclically referenced bones, set the depth value to -1.
    if len(deps):
        for bone in deps:
            bone_depth[bone] = -1

    return bone_depth


class VIEW3D_OT_rig_paste_pose(bpy.types.Operator):
    bl_idname = 'view3d.rig_paste_pose'
    bl_label = 'Copy Pose (World Space)'
    bl_description = 'Paste pose (world space)'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if not obj or not obj.type == 'ARMATURE':
            return False

        if context.mode != 'POSE':
            return False

        return True

    def execute(self, context):
        try:
            data = json.loads(context.window_manager.clipboard)
        except json.decoder.JSONDecodeError:
            return {'CANCELLED'}
        else:
            obj = context.active_object
            bones = obj.pose.bones
            bone_depth = _dependence_depth(obj)

            # Create a dict of bones with depth as a key.
            depth_bone = {}

            for bone in data.keys():
                if bone not in bones:
                    continue

                depth = bone_depth[bone]

                if depth not in depth_bone:
                    depth_bone[depth] = []

                depth_bone[depth].append(bone)

            # Apply the poses in order from the shallowest bone in depth.
            sorted_depth = sorted(depth_bone.keys(), key=lambda d: d)

            for depth in sorted_depth:
                for bone in depth_bone[depth]:
                    b = bones[bone]
                    m = mathutils.Matrix(data[bone]['matrix'])

                    b.matrix = obj.convert_space(
                        pose_bone=b, matrix=m,
                        from_space=data[bone]['space'], to_space='POSE'
                    )

                context.view_layer.update()

        return {'FINISHED'}


class VIEW3D_OT_rig_copy_whole_pose(bpy.types.Operator):
    bl_idname = 'view3d.rig_copy_whole_pose'
    bl_label = 'Copy Whole Pose'
    bl_description = 'Copy pose including unselected bones'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if not obj or not obj.type == 'ARMATURE':
            return False

        if context.mode != 'POSE':
            return False

        return True

    def execute(self, context):
        obj = context.active_object
        bones = obj.pose.bones
        selection = {}
        layers = [False] * 32

        for b in bones:
            selection[b.name] = b.bone.select
            b.bone.select = bool(re.match('CTR_.*', b.name))

        for i in range(32):
            layers[i] = obj.data.layers[i]
            obj.data.layers[i] = True

        bpy.ops.pose.copy()

        for b in bones:
            b.bone.select = selection[b.name]

        for i in range(32):
            obj.data.layers[i] = layers[i]

        return {'FINISHED'}


class VIEW3D_OT_rig_show_animated_bones(bpy.types.Operator):
    bl_idname = 'view3d.rig_show_animated_bones'
    bl_label = 'Show animated bones'
    bl_description = 'Show animated bones'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if not obj or not obj.type == 'ARMATURE':
            return False

        if context.mode != 'POSE':
            return False

        if not obj.animation_data or not obj.animation_data.action:
            return False

        return True

    def execute(self, context):
        obj = context.active_object
        data = obj.data
        animated_bones = set()

        for f in obj.animation_data.action.fcurves:
            m = re.findall(r'CTR_[^"]+', f.data_path)

            if m and m[0] in data.bones:
                animated_bones.add(m[0])

        layers = [False] * 32

        for b in data.bones:
            if not re.match('CTR_.*', b.name):
                continue

            if b.name not in animated_bones:
                b.hide = True

                continue

            b.hide = False

            for i in range(32):
                layers[i] |= b.layers[i]

        for i in range(32):
            data.layers[i] = layers[i]

        return {'FINISHED'}


UI_CONTENTS = {}

# Common
UI_CONTENTS[''] = {
    '': {
        '["quality"]': ('Quality', 'Quality', '', 500, 1.0),
        '["preview_quality"]': ('Quality', 'Preview Quality', '', 501, 1.0)
    },
    '$view3d.rig_show_animated_bones': {
        '': ('Tool', 'Show Animated Bones', 'HIDE_OFF', 0, 1.0)
    },
    '$view3d.rig_copy_pose': {
        '': ('Tool', 'Copy Pose', 'COPYDOWN', 1, 1.0)
    },
    '$view3d.rig_paste_pose': {
        '': ('Tool', 'Paste Pose', 'PASTEDOWN', 1, 1.0)
    },
    '$view3d.rig_copy_whole_pose': {
        '': ('Tool', 'Copy Whole Pose', 'COPYDOWN', 1, 1.0)
    },
    '$view3d.rig_attach_light': {
        '': ('Tool', 'Attach Light', 'LIGHT', 2, 1.0)
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
        ui_utils.collect_contents(contents, obj, props)

        col = self.layout.column(align=True)
        ui_utils.draw_contents(col, contents)
