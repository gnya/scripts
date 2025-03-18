import re


def _switch_lr_callback(m):
    lr = m.group(2)
    pair_lr = 'L' if lr == 'R' else 'R'

    return f'{m.group(1)}{pair_lr}{m.group(3)}'


def switch_lr(name):
    exp = r'(\.)([LR])([$-\/:-?{-~!"^_`\[\]\s]|$)'

    return re.sub(exp, _switch_lr_callback, name)


def is_symmetrical(a, b, properties, symmetrical_properties):
    for p in properties:
        v_a, v_b = getattr(a, p), getattr(b, p)

        if v_a != v_b:
            if type(v_a) is float:
                if abs(v_a - v_b) > 1.0e-6:
                    return False, p
            else:
                return False, p

    for p in symmetrical_properties:
        if getattr(a, p) != switch_lr(getattr(b, p)):
            return False, p

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
        # check "to" properties
        #  only when useing local space,
        #  considering other case is too complicated
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
                or ((a.map_to_x_from in ['Y', 'Z']) and from_rot):
            a_to_max_x, a_to_min_x = a_to_min_x, a_to_max_x

        if (a.map_to_y_from == 'X' and from_loc) \
                or ((a.map_to_y_from == ['Y', 'Z']) and from_rot):
            a_to_max_y, a_to_min_y = a_to_min_y, a_to_max_y

        if (a.map_to_z_from == 'X' and from_loc) \
                or ((a.map_to_z_from == ['Y', 'Z']) and from_rot):
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
                'head_tail', 'mix_mode',
                'remove_target_shear', 'use_bbone_shape'
            ], ['subtarget'])
        case 'DAMPED_TRACK':
            return is_symmetrical(a, b, [
                'head_tail', 'target', 'track_axis', 'use_bbone_shape'
            ], ['subtarget'])
        case 'LOCKED_TRACK':
            return is_symmetrical(a, b, [
                'head_tail', 'lock_axis', 'target',
                'track_axis', 'use_bbone_shape'
            ], ['subtarget'])
        case 'IK':
            return is_symmetrical(a, b, [
                'chain_count', 'distance', 'ik_type', 'iterations',
                'lock_location_x', 'lock_location_y', 'lock_location_z',
                'lock_rotation_x', 'lock_rotation_y', 'lock_rotation_z',
                'orient_weight', 'pole_angle', 'pole_target',
                'reference_axis', 'limit_mode',
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
                'use_invert_cull', 'use_project_opposite', 'use_track_normal',
                'wrap_mode'
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


def symmetrical_bone(bone, bones):
    m = re.match(r'.*\.([LR]).*', bone.name)

    if m:
        pair_name = switch_lr(bone.name)
        pair_bone = bones.get(pair_name)

        return pair_bone, True

    return None, False


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
