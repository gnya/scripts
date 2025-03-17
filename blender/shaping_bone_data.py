import bpy
import re
import math


# Rule1: Deform bone's name must start with "DEF"
def rule1(bone, fix):
    if bone.use_deform:
        if not re.match('DEF_.*', bone.name):
            print(f'Rule1: {bone.name}: Deform bone\'s name must start with "DEF"')

            if fix:
                bone.use_deform = False

            return False

    return True


# Rule2: Armature target must have subtarget and use "Pose Space" instead of "World Space"
def rule2(bone, constraint, fix):
    notice_types = [
        'COPY_LOCATION',
        'COPY_ROTATION',
        'COPY_SCALE',
        'COPY_TRANSFORMS',
        'LIMIT_DISTANCE',
        'TRACK_TO',
        'TRANSFORM'
    ]

    ignore_types = [
        'DAMPED_TRACK',
        'LOCKED_TRACK',
        'IK',
        'LIMIT_LOCATION',
        'LIMIT_SCALE',
        'LIMIT_ROTATION',
        'SHRINKWRAP',
        'STRETCH_TO'
    ]

    if constraint.type in notice_types:
        if constraint.target.type != 'ARMATURE':
            return True

        if not constraint.subtarget:
            print(f'Rule2: {bone.name}: Target must have target bone as subtarget to use "Pose Space": {constraint.name}')

            if fix:
                print(f'WARNING(Rule2): {bone.name}: Can\'t use fix option for this: {constraint.name}')

            return False

        if constraint.target_space == 'WORLD':
            print(f'Rule2: {bone.name}: Target space must use "Pose Space" instead of "World Space": {constraint.name}')

            if fix:
                constraint.target_space = 'POSE'

            return False
    elif constraint.type not in ignore_types:
        print(f'WARNING(Rule2): {bone.name}: Non supported constraint type: {constraint.type}')

        return False

    return True


# Rule3: Owner must use "Pose Space" instead of "World Space"
def rule3(bone, constraint, fix):
    notice_types = [
        'COPY_LOCATION',
        'COPY_ROTATION',
        'COPY_SCALE',
        'COPY_TRANSFORMS',
        'LIMIT_DISTANCE',
        'LIMIT_LOCATION',
        'LIMIT_SCALE',
        'LIMIT_ROTATION',
        'TRACK_TO',
        'TRANSFORM'
    ]

    ignore_types = [
        'DAMPED_TRACK',
        'LOCKED_TRACK',
        'IK',
        'SHRINKWRAP',
        'STRETCH_TO'
    ]

    if constraint.type in notice_types:
        if constraint.owner_space == 'WORLD':
            print(f'Rule3: {bone.name}: Owner space must use "Pose Space" instead of "World Space": {constraint.name}')

            if fix:
                constraint.owner_space = 'POSE'

            return False
    elif constraint.type not in ignore_types:
        print(f'WARNING(Rule3): {bone.name}: Non supported constraint type: {constraint.type}')

        return False

    return True


# Rule4: Armature target must have subtarget
def rule4(bone, constraint):
    notice_types = [
        'COPY_LOCATION',
        'COPY_ROTATION',
        'COPY_SCALE',
        'COPY_TRANSFORMS',
        'DAMPED_TRACK',
        'LOCKED_TRACK',
        'IK',
        'LIMIT_DISTANCE',
        'STRETCH_TO',
        'TRACK_TO',
        'TRANSFORM'
    ]

    ignore_types = [
        'LIMIT_LOCATION',
        'LIMIT_SCALE',
        'LIMIT_ROTATION',
        'SHRINKWRAP'
    ]

    if constraint.type in notice_types:
        if constraint.target.type != 'ARMATURE':
            return True

        if not constraint.subtarget:
            print(f'Rule4: {bone.name}: Target must have target bone as subtarget: {constraint.name}')

            return False
    elif constraint.type not in ignore_types:
        print(f'WARNING(Rule4): {bone.name}: Non supported constraint type: {constraint.type}')

        return False

    return True


def has_driver(armature, bone, constraint, prop_name):
    path = f'pose.bones["{bone.name}"].constraints["{constraint.name}"].{prop_name}'

    for d in armature.animation_data.drivers:
        if d.data_path == path:
            return True

    return False


# Rule5: Constraint's name rule
def rule5(armature, bone, constraint, fix):
    constraint_names = {
        'COPY_LOCATION': 'Copy Location',
        'COPY_ROTATION': 'Copy Rotation',
        'COPY_SCALE': 'Copy Scale',
        'COPY_TRANSFORMS': 'Copy Transforms',
        'DAMPED_TRACK': 'Damped Track',
        'LOCKED_TRACK': 'Locked Track',
        'IK': 'IK',
        'LIMIT_DISTANCE': 'Limit Distance',
        'LIMIT_LOCATION': 'Limit Location',
        'LIMIT_SCALE': 'Limit Scale',
        'LIMIT_ROTATION': 'Limit Rotation',
        'SHRINKWRAP': 'Shrinkwrap',
        'STRETCH_TO': 'Stretch To',
        'TRACK_TO': 'Track To',
        'TRANSFORM': 'Transformation'
    }

    if constraint.type in constraint_names.keys():
        name = constraint_names[constraint.type]
        info = []

        m = re.match(r'.*(\s\(|,\s)(X|Y|Z|FK|IK),?.*\)', constraint.name)

        if m:
            info.append(m.group(2))

        if hasattr(constraint, 'subtarget') and constraint.subtarget:
            info.append(constraint.subtarget)

        if hasattr(constraint, 'influence') and constraint.influence < 1.0:
            if not has_driver(armature, bone, constraint, 'influence'):
                digit = 0

                if constraint.influence > 0.0:
                    digit = math.floor(math.log10(constraint.influence))

                info.append(f'{constraint.influence:.{-digit}f}')

        suffix = ', '.join(info)

        if suffix:
            name += f' ({suffix})'

        if name != constraint.name:
            print(f'Rule5: {bone.name}: Suggested constraint name change: {constraint.name} -> {name}')

            if fix:
                constraint.name = name

            return False
    else:
        print(f'WARNING(Rule5): {bone.name}: Non supported constraint type: {constraint.type}')

        return False

    return True


# Rule6: Constraint's panel must be shrinked
def rule6(bone, constraint, fix, mute):
    if constraint.show_expanded:
        if not mute:
            print(f'Rule6: {bone.name}: Constraint\'s panel must be shrinked: {constraint.name}')

        if fix:
            constraint.show_expanded = False

        return False

    return True


# Rule7: B-Bone's name rule
def rule7(armature, bone, fix):
    if bone.bbone_segments > 1:
        m = re.match(r'DEF_.*(_b)\b.*', bone.name)

        if m:
            s = m.span(1)
            name = bone.name[:s[0]] + bone.name[s[1]:]
            print(f'Rule7: {bone.name}: Suggested bone name change: {name}')

            if fix:
                if name not in armature.data.bones:
                    bone.name = name
                else:
                    print(f'WARNING(Rule7): {bone.name}: Can\'t use fix option for this: Bone "{name}" is already exists')

            return False

    return True


# Rule8: Do not lock properties except at "CTR" bone
def rule8(bone, fix):
    if not re.match('CTR_.*', bone.name):
        if any(bone.lock_location):
            print(f'Rule8: {bone.name}: Do not lock location properties except at "CTR" bone')

            if fix:
                bone.lock_location = (False, False, False)

            return False

        if any(bone.lock_rotation):
            print(f'Rule8: {bone.name}: Do not lock rotation properties except at "CTR" bone')

            if fix:
                bone.lock_rotation = (False, False, False)

            return False

        if bone.lock_rotation_w:
            print(f'Rule8: {bone.name}: Do not lock rotation_w properties except at "CTR" bone')

            if fix:
                bone.lock_rotation_w = False

            return False

        if any(bone.lock_scale):
            print(f'Rule8: {bone.name}: Do not lock scale properties except at "CTR" bone')

            if fix:
                bone.lock_scale = (False, False, False)

            return False

    return True


def _switch_lr_callback(m):
    lr = m.group(2)
    mirror_lr = 'L' if lr == 'R' else 'R'

    return f'{m.group(1)}{mirror_lr}{m.group(3)}'


def switch_lr(name):
    exp = r'(\.)([LR])([$-\/:-?{-~!"^_`\[\]\s]|$)'

    return re.sub(exp, _switch_lr_callback, name)


def symmetrical_bone(bone, bones):
    m = re.match(r'.*\.([LR]).*', bone.name)

    if m:
        mirror_name = switch_lr(bone.name)
        mirror_bone = bones.get(mirror_name)

        return mirror_bone, True

    return None, False


# Rule9: Check bone is symmetrical
def rule9(bone, mirror_bone):
    if not mirror_bone:
        print(f'Rule9: {bone.name}: There is no bone to by symmetrical with "{bone.name}"')

        return False

    return True


def is_symmetrical_driver_variable(a, b):
    if a.type != b.type:
        return False, 'Type'

    if len(a.targets) != len(b.targets):
        return False, 'Count of Targets'

    for (a_t, b_t) in zip(a.targets, b.targets):
        if a_t.bone_target != switch_lr(b_t.bone_target):
            return False, 'Bone Target'

        if a_t.data_path != switch_lr(b_t.data_path):
            return False, 'Data Path'

        if a_t.id.name != switch_lr(b_t.id.name):
            return False, 'ID Name'

        if a_t.rotation_mode != b_t.rotation_mode:
            return False, 'Rotation Mode'

        if a_t.transform_space != b_t.transform_space:
            return False, 'Transform Space'

        if a_t.transform_type != b_t.transform_type:
            return False, 'Transform Type'

    return True, ''


# Rule10: Check bone driver is symmetrical
def rule10(driver, drivers):
    index = driver.array_index
    path = driver.data_path
    m = re.match(r'pose\.bones\["([^\]]*)"\]', path)

    if m:
        bone_name = m.group(1)
        mirror_path = switch_lr(path)
        mirror_driver = drivers.find(mirror_path, index=index)

        if not mirror_driver:
            print(f'Rule10: {bone_name}: There is no driver to by symmetrical with "{path}"')

            return False

        variables = driver.driver.variables
        mirror_variables = mirror_driver.driver.variables

        for v in variables:
            mirror_v = mirror_variables.get(switch_lr(v.name))

            if not mirror_v:
                print(f'Rule10: {bone_name}: There is no driver variable "{v.name}" to by symmetrical with')

                return False

            is_mirror, s = is_symmetrical_driver_variable(v, mirror_v)

            if not is_mirror:
                print(f'Rule10: {bone_name}: Driver variable "{v.name}" is not symmetrical: {s}')

                return False

    return True


def is_symmetrical(a, b, properties, symmetrical_properties):
    for p in properties:
        v_a, v_b = getattr(a, p), getattr(b, p)

        if v_a != v_b:
            if type(v_a) is float:
                if abs(v_a - v_b) > 1.0e-6:
                    return False, f'{a.name} -> {p}'
            else:
                return False, f'{a.name} -> {p}'

    for p in symmetrical_properties:
        if getattr(a, p) != switch_lr(getattr(b, p)):
            return False, f'{a.name} -> {p}'

    return True, ''


def is_symmetrical_transform_constraint(a, b):
    to_loc = a.map_to == 'LOCATION'
    to_rot = a.map_to == 'ROTATION'
    from_loc = a.map_from == 'LOCATION'
    from_rot = a.map_from == 'ROTATION'

    # check "from" properties
    if a.from_max_x != -b.from_min_x:
        return False, 'from_max_x'
    if a.from_min_x != -b.from_max_x:
        return False, 'from_min_x'
    if a.from_max_y != -b.from_min_y:
        return False, 'from_max_y'
    if a.from_min_y != -b.from_max_y:
        return False, 'from_min_y'
    if a.from_max_z != -b.from_min_z:
        return False, 'from_max_z'
    if a.from_min_z != -b.from_max_z:
        return False, 'from_min_z'

    if a.target_space == a.owner_space or a.target_space == 'LOCAL':
        # check "to" properties (only when useing local space, considering other case is too complicated)
        a_to_max_x = -a.to_max_x if to_loc \
            else (a.to_max_x_rot if to_rot else a.to_max_x_scale)
        a_to_max_y = a.to_max_y if to_loc \
            else (-a.to_max_y_rot if to_rot else a.to_max_y_scale)
        a_to_max_z = a.to_max_z if to_loc \
            else (-a.to_max_z_rot if to_rot else a.to_max_z_scale)

        a_to_min_x = -a.to_min_x if to_loc \
            else (a.to_min_x_rot if to_rot else a.to_min_x_scale)
        a_to_min_y = a.to_min_y if to_loc \
            else (-a.to_min_y_rot if to_rot else a.to_min_y_scale)
        a_to_min_z = a.to_min_z if to_loc \
            else (-a.to_min_z_rot if to_rot else a.to_min_z_scale)

        if (a.map_to_x_from == 'X' and from_loc) \
           or ((a.map_to_x_from == 'Y' or a.map_to_x_from == 'Z') and from_rot):
            a_to_max_x, a_to_min_x = a_to_min_x, a_to_max_x

        if (a.map_to_y_from == 'X' and from_loc) \
           or ((a.map_to_y_from == 'Y' or a.map_to_y_from == 'Z') and from_rot):
            a_to_max_y, a_to_min_y = a_to_min_y, a_to_max_y

        if (a.map_to_z_from == 'X' and from_loc) \
           or ((a.map_to_z_from == 'Y' or a.map_to_z_from == 'Z') and from_rot):
            a_to_max_z, a_to_min_z = a_to_min_z, a_to_max_z

        b_to_max_x = b.to_max_x if to_loc \
            else (b.to_max_x_rot if to_rot else b.to_max_x_scale)
        b_to_max_y = b.to_max_y if to_loc \
            else (b.to_max_y_rot if to_rot else b.to_max_y_scale)
        b_to_max_z = b.to_max_z if to_loc \
            else (b.to_max_z_rot if to_rot else b.to_max_z_scale)

        b_to_min_x = b.to_min_x if to_loc \
            else (b.to_min_x_rot if to_rot else b.to_min_x_scale)
        b_to_min_y = b.to_min_y if to_loc \
            else (b.to_min_y_rot if to_rot else b.to_min_y_scale)
        b_to_min_z = b.to_min_z if to_loc \
            else (b.to_min_z_rot if to_rot else b.to_min_z_scale)

        if a_to_max_x != b_to_max_x:
            return False, 'to_max_x/to_max_x_rot/to_max_x_scale'
        if a_to_min_x != b_to_min_x:
            return False, 'to_min_x/to_min_x_rot/to_min_x_scale'
        if a_to_max_y != b_to_max_y:
            return False, 'to_max_y/to_max_y_rot/to_max_y_scale'
        if a_to_min_y != b_to_min_y:
            return False, 'to_min_y/to_min_y_rot/to_min_y_scale'
        if a_to_max_z != b_to_max_z:
            return False, 'to_max_z/to_max_z_rot/to_max_z_scale'
        if a_to_min_z != b_to_min_z:
            return False, 'to_min_z/to_min_z_rot/to_min_z_scale'

    properties = [
        'from_max_x_rot', 'from_max_x_scale',
        'from_max_y', 'from_max_y_scale',
        'from_max_z', 'from_max_z_scale',
        'from_min_x_rot', 'from_min_x_scale',
        'from_min_y', 'from_min_y_scale',
        'from_min_z', 'from_min_z_scale',
        'from_rotation_mode', 'map_from', 'map_to', 'target',
        'map_to_x_from', 'map_to_y_from', 'map_to_z_from',
        'mix_mode', 'mix_mode_rot', 'mix_mode_scale',
        'to_euler_order', 'use_motion_extrapolate'
    ]

    if not to_loc:
        properties += [
            'to_max_x', 'to_max_y', 'to_max_z',
            'to_min_x', 'to_min_y', 'to_min_z'
        ]

    if not to_rot:
        properties += [
            'to_max_x_rot', 'to_max_y_rot', 'to_max_z_rot',
            'to_min_x_rot', 'to_min_y_rot', 'to_min_z_rot'
        ]

    if to_loc or to_rot:
        properties += [
            'to_max_x_scale', 'to_max_y_scale', 'to_max_z_scale',
            'to_min_x_scale', 'to_min_y_scale', 'to_min_z_scale'
        ]

    return is_symmetrical(a, b, properties, ['subtarget'])


def is_symmetrical_constraint(a, b):
    res, s = is_symmetrical(a, b, [
        'enabled', 'error_location', 'error_rotation',
        'influence', 'is_override_data', 'is_valid', 'mute',
        'owner_space', 'space_object', 'target_space', 'type'
    ], ['name', 'space_subtarget'])

    if not res:
        return False, s

    match a.type:
        case 'COPY_LOCATION':
            return is_symmetrical(a, b, [
                'head_tail', 'invert_x', 'invert_y', 'invert_z', 'target',
                'use_bbone_shape', 'use_offset', 'use_x', 'use_y', 'use_z'
            ], ['subtarget'])
        case 'COPY_ROTATION':
            return is_symmetrical(a, b, [
                'euler_order', 'invert_x', 'invert_y', 'invert_z', 'mix_mode',
                'target', 'use_offset', 'use_x', 'use_y', 'use_z'
            ], ['subtarget'])
        case 'COPY_SCALE':
            return is_symmetrical(a, b, [
                'power', 'target', 'use_add', 'use_make_uniform',
                'use_offset', 'use_x', 'use_y', 'use_z'
            ], ['subtarget'])
        case 'COPY_TRANSFORMS':
            return is_symmetrical(a, b, [
                'head_tail', 'mix_mode', 'remove_target_shear', 'use_bbone_shape'
            ], ['subtarget'])
        case 'DAMPED_TRACK':
            return is_symmetrical(a, b, [
                'head_tail', 'target', 'track_axis', 'use_bbone_shape'
            ], ['subtarget'])
        case 'LOCKED_TRACK':
            return is_symmetrical(a, b, [
                'head_tail', 'lock_axis', 'target', 'track_axis', 'use_bbone_shape'
            ], ['subtarget'])
        case 'IK':
            return is_symmetrical(a, b, [
                'chain_count', 'distance', 'ik_type', 'iterations', 'limit_mode',
                'lock_location_x', 'lock_location_y', 'lock_location_z',
                'lock_rotation_x', 'lock_rotation_y', 'lock_rotation_z',
                'orient_weight', 'pole_angle', 'pole_target', 'reference_axis',
                'target', 'use_location', 'use_rotation',
                'use_stretch', 'use_tail', 'weight'
            ], ['pole_subtarget', 'subtarget'])
        case 'LIMIT_DISTANCE':
            return is_symmetrical(a, b, [
                'distance', 'head_tail', 'limit_mode', 'target',
                'use_bbone_shape', 'use_transform_limit'
            ], ['subtarget'])
        case 'LIMIT_LOCATION':
            return is_symmetrical(a, b, [
                'max_x', 'max_y', 'max_z', 'min_x', 'min_y', 'min_z',
                'use_max_x', 'use_max_y', 'use_max_z',
                'use_min_x', 'use_min_y', 'use_min_z', 'use_transform_limit'
            ], [])
        case 'LIMIT_SCALE':
            return is_symmetrical(a, b, [
                'max_x', 'max_y', 'max_z', 'min_x', 'min_y', 'min_z',
                'use_max_x', 'use_max_y', 'use_max_z',
                'use_min_x', 'use_min_y', 'use_min_z', 'use_transform_limit'
            ], [])
        case 'LIMIT_ROTATION':
            if a.max_y != -b.min_y or a.min_y != -b.max_y:
                return False, 'min_y/max_y'

            if a.max_z != -b.min_z or a.min_z != -b.max_z:
                return False, 'min_z/max_z'

            return is_symmetrical(a, b, [
                'euler_order', 'max_x', 'min_x', 'use_transform_limit',
                'use_limit_x', 'use_limit_y', 'use_limit_z'
            ], [])
        case 'SHRINKWRAP':
            return is_symmetrical(a, b, [
                'cull_face', 'distance', 'project_axis', 'project_axis_space',
                'project_limit', 'shrinkwrap_type', 'target', 'track_axis',
                'use_invert_cull', 'use_project_opposite', 'use_track_normal', 'wrap_mode'
            ], [])
        case 'STRETCH_TO':
            return is_symmetrical(a, b, [
                'bulge', 'bulge_max', 'bulge_min', 'bulge_smooth', 'head_tail',
                'keep_axis', 'rest_length', 'target', 'use_bbone_shape',
                'use_bulge_max', 'use_bulge_min', 'volume'
            ], ['subtarget'])
        case 'TRACK_TO':
            return is_symmetrical(a, b, [
                'head_tail', 'target', 'track_axis', 'up_axis',
                'use_bbone_shape', 'use_target_z'
            ], ['subtarget'])
        case 'TRANSFORM':
            return is_symmetrical_transform_constraint(a, b)

    return False, f'Not Supported: {a.type}'


# Rule11: Check bone constraint is symmetrical
def rule11(bone, mirror_bone):
    if len(bone.constraints) != len(mirror_bone.constraints):
        print(f'Rule11: {bone.name}: Count of bone constraints is not symmetrical')

        return False

    for (a_c, b_c) in zip(bone.constraints, mirror_bone.constraints):
        is_mirror, s = is_symmetrical_constraint(a_c, b_c)

        if not is_mirror:
            print(f'Rule11: {bone.name}: Bone constraint is not symmetrical: {s}')

            return False

    return True


# Rule12: Check not used customeshapes
def rule12(armatures):
    used_customshapes = set()

    for a in armatures:
        for b in a.pose.bones:
            if b.custom_shape:
                used_customshapes.add(b.custom_shape.name)

    exist_customshapes = set()

    for o in bpy.data.objects:
        m = re.match(r'^[^_.]*_CUSTOMSHAPE.*$', o.name)

        if m:
            exist_customshapes.add(o.name)

    not_used_customshapes = exist_customshapes - used_customshapes

    if not_used_customshapes:
        print(f'Rule12: There are custom shapes that didn\'t used: {not_used_customshapes}')

        return False

    return True


# Rule13: Check bone parent is symmetrical
def rule13(bone, mirror_bone):
    if not bone.parent:
        return True

    if not mirror_bone.parent or bone.parent.name != switch_lr(mirror_bone.parent.name):
        print(f'Rule13: {bone.name}: Bone parent is not symmetrical')

        return False

    return True


# Rule14: Modifier's name rule
def rule14(obj, modifier, fix):
    modifier_names = {
        'MIRROR': 'Mirror',
        'SOLIDIFY': 'Solidify',
        'SURFACE_DEFORM': 'Surface Deform',
        'MASK': 'Mask',
        'DATA_TRANSFER': 'Data Transfer',
        'CAST': 'Cast',
        'LATTICE': 'Lattice',
        'SUBSURF': 'Subdivision',
        'HOOK': 'Hook',
        'ARMATURE': 'Armature',
        'NODES': 'Geometry Nodes'
    }

    if modifier.type in modifier_names.keys():
        name = modifier_names[modifier.type]
        info = []

        if hasattr(modifier, 'object'):
            info.append(modifier.object.name)

        if hasattr(modifier, 'target'):
            info.append(modifier.target.name)

        if hasattr(modifier, 'subtarget'):
            info.append(modifier.subtarget)

        if modifier.type == 'MASK' and hasattr(modifier, 'vertex_group'):
            info.append(modifier.vertex_group)

        if modifier.type == 'NODES':
            name = modifier.node_group.name

            keys = []
            items = []

            for i in modifier.node_group.inputs[1:]:
                keys.append(i.name.lower())

            for k, v in modifier.items():
                if re.match(r'^Input_\d*$', k):
                    items.append(v)

            for k, v in zip(keys, items):
                if k == 'target':
                    info.append(v.name)

        suffix = ', '.join(info)

        if suffix:
            name += f' ({suffix})'

        if name != modifier.name:
            print(f'Rule14: {obj.name}: Suggested modifier name change: {modifier.name} -> {name}')

            if fix:
                modifier.name = name
    else:
        print(f'WARNING(Rule14): {obj.name}: Non supported modifier type: {modifier.type}')

        return False

    return True


def reset_properties(data, properties, defaults):
    info = []

    for p in properties:
        prop = data.rna_type.properties[p]
        value = getattr(data, p)
        default = defaults[p] if p in defaults else prop.default

        if value != default:
            info.append(f'{p}({value} != {default})')
            setattr(data, p, default)

    if info:
        return False, ', '.join(info)

    return True, ''


# Rule15: Check IK properties in bones that is't in IK chain
def rule15(bone):
    if not bone.is_in_ik_chain:
        is_default, s = reset_properties(bone, [
            'ik_linear_weight', 'ik_max_x', 'ik_max_y', 'ik_max_z',
            'ik_min_x', 'ik_min_y', 'ik_min_z', 'ik_rotation_weight',
            'ik_stiffness_x', 'ik_stiffness_y', 'ik_stiffness_z',
            'ik_stretch', 'use_ik_rotation_control', 'use_ik_linear_control',
            'use_ik_limit_x', 'use_ik_limit_y', 'use_ik_limit_z',
            'lock_ik_x', 'lock_ik_y', 'lock_ik_z'
        ], {
            'ik_max_x': 3.1415927410125732,
            'ik_max_y': 3.1415927410125732,
            'ik_max_z': 3.1415927410125732,
            'ik_min_x': -3.1415927410125732,
            'ik_min_y': -3.1415927410125732,
            'ik_min_z': -3.1415927410125732
        })

        if not is_default:
            print(f'Rule15: {bone.name}: Use default value: {s}')

            return False

    return True


if __name__ == '__main__':
    fix = True
    armatures = []

    for o in bpy.context.selected_objects:
        if o.type == 'ARMATURE':
            armatures.append(o)

    rule12(armatures)

    for a in armatures:
        for b in a.data.bones:
            rule1(b, fix)
            rule7(a, b, fix)

        for b in a.pose.bones:
            rule8(b, fix)
            rule15(b)
            sb = a.pose.bones.get(switch_lr(b.name))
            rule9(b, sb)
            rule11(b, sb)
            rule13(b, sb)

            for c in b.constraints:
                rule2(b, c, fix)
                rule3(b, c, fix)
                rule4(b, c)
                rule5(a, b, c, fix)
                rule6(b, c, fix, True)

        if a.animation_data:
            drivers = a.animation_data.drivers

            for d in drivers:
                rule10(d, drivers)

        for c in a.children_recursive:
            for m in c.modifiers:
                rule14(c, m, fix)
