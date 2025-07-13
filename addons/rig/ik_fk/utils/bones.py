import re


def _check_ik_fk_bone(bone):
    name = bone.name if bone else ''
    match = re.match(r'CTR_(.+)_(ik|fk).*\.(L|R)', name)

    if not match:
        return False, '', '', ''

    group = match.group(1)
    ik_or_fk = match.group(2)
    l_or_r = match.group(3)

    if group not in ['arm', 'leg']:
        if group in ['hand']:
            group = 'arm'
        elif group in ['foot', 'toe', 'heel', 'foot_spin']:
            group = 'leg'
        else:
            group = ''

    if ik_or_fk not in ['ik', 'fk']:
        ik_or_fk = ''

    if l_or_r not in ['L', 'R']:
        l_or_r = ''

    if group and ik_or_fk and l_or_r:
        return True, group, ik_or_fk, l_or_r

    return False, '', '', ''


def check_ik_fk_bones(bones):
    groups = set()

    for b in bones:
        check, group, ikfk, lr = _check_ik_fk_bone(b)

        if check:
            groups.add((b.id_data, group, ikfk, lr))

    return groups


def _ik_fk_arm_bone_names(lr):
    return {
        'parent': f'MCH_arm_parent.{lr}',
        'ik_pole': f'CTR_arm_ik_pole.{lr}',
        'ik_pole_parent': f'MCH_arm_ik_pole.{lr}',
        'ik_length': f'CTR_arm_ik_length.{lr}',
        'ik_parent': f'MCH_arm_ik_parent.{lr}',
        'ik_target': f'MCH_arm_ik_target.{lr}',
        'ik_1': f'MCH_arm_ik_upperarm.{lr}',
        'ik_2': f'MCH_arm_ik_forearm.{lr}',
        'ik_3': f'CTR_hand_ik.{lr}',
        'fk_length': f'CTR_arm_fk_length.{lr}',
        'fk_1': f'CTR_arm_fk_upperarm.{lr}',
        'fk_2': f'CTR_arm_fk_forearm.{lr}',
        'fk_3': f'CTR_hand_fk.{lr}'
    }


def _ik_fk_leg_bone_names(lr):
    return {
        'parent': f'MCH_leg_parent.{lr}',
        'ik_pole': f'CTR_leg_ik_pole.{lr}',
        'ik_pole_parent': f'MCH_leg_ik_pole.{lr}',
        'ik_length': f'CTR_leg_ik_length.{lr}',
        'ik_parent': f'MCH_leg_ik_parent.{lr}',
        'ik_target': f'MCH_leg_ik_target.{lr}',
        'ik_1': f'MCH_leg_ik_thigh.{lr}',
        'ik_2': f'MCH_leg_ik_shin.{lr}',
        'ik_3': f'CTR_foot_ik.{lr}',
        'ik_3_dash': f'MCH_foot_ik.{lr}',
        'ik_4': f'CTR_toe_ik.{lr}',
        'ik_4_parent': f'MCH_toe_ik.{lr}',
        'ik_heel': f'CTR_heel_ik.{lr}',
        'ik_foot_spin': f'CTR_foot_spin_ik.{lr}',
        'fk_length': f'CTR_leg_fk_length.{lr}',
        'fk_1': f'CTR_leg_fk_thigh.{lr}',
        'fk_2': f'CTR_leg_fk_shin.{lr}',
        'fk_3': f'CTR_foot_fk.{lr}',
        'fk_4': f'CTR_toe_fk.{lr}',
        'fk_4_parent': f'MCH_toe_fk.{lr}'
    }


def ik_fk_bones(armature, group, lr):
    bone_names = {}

    if 'arm' == group:
        bone_names = _ik_fk_arm_bone_names(lr)
    elif 'leg' == group:
        bone_names = _ik_fk_leg_bone_names(lr)

    bones = armature.pose.bones

    ik_fk_bones = {}
    missing_bones = {}

    for k, v in bone_names.items():
        if v in bones:
            ik_fk_bones[k] = bones[v]
        else:
            missing_bones[k] = v

    return ik_fk_bones, missing_bones
