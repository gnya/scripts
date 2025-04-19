import re


def _switch_lr_callback(m):
    lr = m.group(2)
    pair_lr = 'L' if lr == 'R' else 'R'

    return f'{m.group(1)}{pair_lr}{m.group(3)}'


def switch_lr(name):
    exp = r'(\.)([LR])([$-\/:-?{-~!"^_`\[\]\s]|$)'

    return re.sub(exp, _switch_lr_callback, name)


def symmetrical_bone(bone, bones):
    pair_bone = bones.get(switch_lr(bone.name))

    if not pair_bone or pair_bone.name == bone.name:
        return None, False

    return pair_bone, True


def _is_symmetrical(a, b, properties, symmetrical_properties):
    for p in properties:
        v_a, v_b = getattr(a, p), getattr(b, p)

        if v_a is not None:
            if v_b is None:
                return False, p
            elif type(v_a) is float:
                if abs(v_a - v_b) > 1.0e-6:
                    return False, p
            elif v_a != v_b:
                return False, p

    for p in symmetrical_properties:
        v_a, v_b = getattr(a, p), getattr(b, p)

        if v_a is not None:
            if v_b is None:
                return False, p
            elif hasattr(v_a, 'name'):
                if v_a.name != switch_lr(v_b.name):
                    return False, p
            elif v_a != switch_lr(v_b):
                return False, p

    return True, ''


def is_symmetrical_driver_variable(a, b):
    if a.type != b.type:
        return False, 'Type'

    if len(a.targets) != len(b.targets):
        return False, 'Count of Targets'

    info = []

    for (a_t, b_t) in zip(a.targets, b.targets):
        is_pair, s = _is_symmetrical(a_t, b_t, [
            'rotation_mode', 'transform_space', 'transform_type'
        ], [
            'bone_target', 'data_path', 'id'
        ])

        if not is_pair:
            info.append(s)

    return not info, ', '.join(info)


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
                or ((a.map_to_y_from in ['Y', 'Z']) and from_rot):
            a_to_max_y, a_to_min_y = a_to_min_y, a_to_max_y

        if (a.map_to_z_from == 'X' and from_loc) \
                or ((a.map_to_z_from in ['Y', 'Z']) and from_rot):
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
        'from_rotation_mode', 'map_from', 'map_to',
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

    return _is_symmetrical(a, b, properties, ['target', 'subtarget'])


def is_symmetrical_constraint(a, b):
    res, s = _is_symmetrical(a, b, [
        'enabled', 'error_location', 'error_rotation',
        'influence', 'is_override_data', 'is_valid', 'mute',
        'owner_space', 'target_space', 'type'
    ], ['name', 'space_object', 'space_subtarget'])

    if not res:
        return False, s

    match a.type:
        case 'COPY_LOCATION':
            return _is_symmetrical(a, b, [
                'head_tail', 'invert_x', 'invert_y', 'invert_z',
                'use_bbone_shape', 'use_offset', 'use_x', 'use_y', 'use_z'
            ], ['target', 'subtarget'])
        case 'COPY_ROTATION':
            return _is_symmetrical(a, b, [
                'euler_order', 'invert_x', 'invert_y', 'invert_z', 'mix_mode',
                'use_offset', 'use_x', 'use_y', 'use_z'
            ], ['target', 'subtarget'])
        case 'COPY_SCALE':
            return _is_symmetrical(a, b, [
                'power', 'use_add', 'use_make_uniform',
                'use_offset', 'use_x', 'use_y', 'use_z'
            ], ['target', 'subtarget'])
        case 'COPY_TRANSFORMS':
            return _is_symmetrical(a, b, [
                'head_tail', 'mix_mode',
                'remove_target_shear', 'use_bbone_shape'
            ], ['target', 'subtarget'])
        case 'DAMPED_TRACK':
            return _is_symmetrical(a, b, [
                'head_tail', 'track_axis', 'use_bbone_shape'
            ], ['target', 'subtarget'])
        case 'LOCKED_TRACK':
            return _is_symmetrical(a, b, [
                'head_tail', 'lock_axis',
                'track_axis', 'use_bbone_shape'
            ], ['target', 'subtarget'])
        case 'IK':
            return _is_symmetrical(a, b, [
                'chain_count', 'distance', 'ik_type', 'iterations',
                'lock_location_x', 'lock_location_y', 'lock_location_z',
                'lock_rotation_x', 'lock_rotation_y', 'lock_rotation_z',
                'orient_weight', 'pole_angle', 'pole_target',
                'reference_axis', 'limit_mode',
                'use_location', 'use_rotation',
                'use_stretch', 'use_tail', 'weight'
            ], ['pole_subtarget', 'target', 'subtarget'])
        case 'LIMIT_DISTANCE':
            return _is_symmetrical(a, b, [
                'distance', 'head_tail', 'limit_mode',
                'use_bbone_shape', 'use_transform_limit'
            ], ['target', 'subtarget'])
        case 'LIMIT_LOCATION':
            return _is_symmetrical(a, b, [
                'max_x', 'max_y', 'max_z', 'min_x', 'min_y', 'min_z',
                'use_max_x', 'use_max_y', 'use_max_z',
                'use_min_x', 'use_min_y', 'use_min_z', 'use_transform_limit'
            ], [])
        case 'LIMIT_SCALE':
            return _is_symmetrical(a, b, [
                'max_x', 'max_y', 'max_z', 'min_x', 'min_y', 'min_z',
                'use_max_x', 'use_max_y', 'use_max_z',
                'use_min_x', 'use_min_y', 'use_min_z', 'use_transform_limit'
            ], [])
        case 'LIMIT_ROTATION':
            if a.max_y != -b.min_y or a.min_y != -b.max_y:
                return False, 'min_y/max_y'

            if a.max_z != -b.min_z or a.min_z != -b.max_z:
                return False, 'min_z/max_z'

            return _is_symmetrical(a, b, [
                'euler_order', 'max_x', 'min_x', 'use_transform_limit',
                'use_limit_x', 'use_limit_y', 'use_limit_z'
            ], [])
        case 'SHRINKWRAP':
            return _is_symmetrical(a, b, [
                'cull_face', 'distance', 'project_axis', 'project_axis_space',
                'project_limit', 'shrinkwrap_type', 'target', 'track_axis',
                'use_invert_cull', 'use_project_opposite', 'use_track_normal',
                'wrap_mode'
            ], [])
        case 'STRETCH_TO':
            return _is_symmetrical(a, b, [
                'bulge', 'bulge_max', 'bulge_min', 'bulge_smooth', 'head_tail',
                'keep_axis', 'rest_length', 'use_bbone_shape',
                'use_bulge_max', 'use_bulge_min', 'volume'
            ], ['target', 'subtarget'])
        case 'TRACK_TO':
            return _is_symmetrical(a, b, [
                'head_tail', 'track_axis', 'up_axis',
                'use_bbone_shape', 'use_target_z'
            ], ['target', 'subtarget'])
        case 'TRANSFORM':
            return is_symmetrical_transform_constraint(a, b)

    return False, f'Not Supported: {a.type}'
