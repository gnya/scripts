import bpy
import re
import math


def rule1(bone, fix):
    if bone.use_deform:
        if not re.match('DEF_.*', bone.name):
            print(f'Rule1: {bone.name}: Deform bone\'s name must start with "DEF"')

            if fix:
                bone.use_deform = False

            return False

    return True


def rule2(bone, constraint, fix):
    notice_types = [
        'COPY_LOCATION',
        'COPY_ROTATION',
        'COPY_SCALE',
        'COPY_TRANSFORMS',
        'LIMIT_DISTANCE',
        'TRANSFORM'
    ]

    ignore_types = [
        'DAMPED_TRACK',
        'IK',
        'LIMIT_LOCATION',
        'LIMIT_ROTATION',
        'STRETCH_TO'
    ]

    if constraint.type in notice_types:
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


def rule3(bone, constraint, fix):
    notice_types = [
        'COPY_LOCATION',
        'COPY_ROTATION',
        'COPY_SCALE',
        'COPY_TRANSFORMS',
        'LIMIT_DISTANCE',
        'LIMIT_LOCATION',
        'LIMIT_ROTATION',
        'TRANSFORM'
    ]

    ignore_types = [
        'DAMPED_TRACK',
        'IK',
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


def rule4(bone, constraint, fix):
    notice_types = [
        'COPY_LOCATION',
        'COPY_ROTATION',
        'COPY_SCALE',
        'COPY_TRANSFORMS',
        'DAMPED_TRACK',
        'IK',
        'LIMIT_DISTANCE',
        'STRETCH_TO',
        'TRANSFORM'
    ]

    ignore_types = [
        'LIMIT_LOCATION',
        'LIMIT_ROTATION'
    ]

    if constraint.type in notice_types:
        if not constraint.subtarget:
            print(f'Rule4: {bone.name}: Target must have target bone as subtarget: {constraint.name}')

            if fix:
                print(f'WARNING(Rule4): {bone.name}: Can\'t use fix option for this: {constraint.name}')

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


def rule5(armature, bone, constraint, fix):
    constraint_names = {
        'COPY_LOCATION': 'Copy Location',
        'COPY_ROTATION': 'Copy Rotation',
        'COPY_SCALE': 'Copy Scale',
        'COPY_TRANSFORMS': 'Copy Transforms',
        'DAMPED_TRACK': 'Damped Track',
        'IK': 'IK',
        'LIMIT_DISTANCE': 'Limit Distance',
        'LIMIT_LOCATION': 'Limit Location',
        'LIMIT_ROTATION': 'Limit Rotation',
        'STRETCH_TO': 'Stretch To',
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


def rule6(bone, constraint, fix):
    if constraint.show_expanded:
        print(f'Rule6: {bone.name}: Constraint\'s panel must be shrinked: {constraint.name}')

        if fix:
            constraint.show_expanded = False

        return False

    return True


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


if __name__ == '__main__':
    fix = True
    armatures = []

    for o in bpy.context.selected_objects:
        if o.type == 'ARMATURE':
            armatures.append(o)

    for a in armatures:
        for b in a.data.bones:
            rule1(b, fix)
            rule7(a, b, fix)

        for b in a.pose.bones:
            for c in b.constraints:
                rule2(b, c, fix)
                rule3(b, c, fix)
                rule4(b, c, fix)
                rule5(a, b, c, fix)
                rule6(b, c, fix)
