import re


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


def dependence_depth(armature):
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
