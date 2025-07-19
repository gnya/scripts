import re


def _bones_used_in_driver(driver, armature):
    used_bones = set()

    for v in driver.driver.variables:
        for t in v.targets:
            if t.id != armature:
                continue

            if t.bone_target:
                used_bones.add(t.bone_target)

            m = re.search(r'bones\["([^"]+)"\]', t.data_path)

            if m:
                used_bones.add(m.group(1))

    return used_bones


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


def _bones_used_in_modifier(modifier, armature):
    used_bones = set()

    match modifier.type:
        case 'MIRROR':
            pass
        case 'SOLIDIFY':
            pass
        case 'SURFACE_DEFORM':
            pass
        case 'MASK':
            pass
        case 'DATA_TRANSFER':
            pass
        case 'CAST':
            pass
        case 'LATTICE':
            pass
        case 'SOFT_BODY':
            pass
        case 'SUBSURF':
            pass
        case 'HOOK':
            if modifier.object == armature and modifier.subtarget:
                used_bones.add(modifier.subtarget)
        case 'ARMATURE':
            pass
        case 'NODES':
            pass

    return used_bones


def bones_used_in_object(obj, armature):
    used_bones = set()

    if obj.type == 'ARMATURE':
        for b in obj.data.bones:
            if obj == armature:
                if b.bbone_handle_type_start != 'AUTO' and b.bbone_custom_handle_start:
                    used_bones.add(b.bbone_custom_handle_start.name)

                if b.bbone_handle_type_start != 'AUTO' and b.bbone_custom_handle_end:
                    used_bones.add(b.bbone_custom_handle_end.name)

        for b in obj.pose.bones:
            if obj == armature and b.custom_shape_transform:
                used_bones.add(b.custom_shape_transform.name)

            for c in b.constraints:
                used_bones |= _bones_used_in_constraint(c, armature)

    if obj.vertex_groups:
        has_armature = False

        for m in obj.modifiers:
            if m.type == 'ARMATURE' and m.object == armature:
                has_armature = True

        if has_armature:
            for g in obj.vertex_groups:
                if g.name in armature.data.bones:
                    used_bones.add(g.name)

    for c in obj.constraints:
        used_bones |= _bones_used_in_constraint(c, armature)

    if obj.animation_data:
        for d in obj.animation_data.drivers:
            used_bones |= _bones_used_in_driver(d, armature)

    for m in obj.modifiers:
        used_bones |= _bones_used_in_modifier(m, armature)

    return used_bones
