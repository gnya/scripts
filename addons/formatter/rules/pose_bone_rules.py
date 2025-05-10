import re
import mathutils
from . import utils
from .rules import Report, PoseBoneRule


# Check IK properties in bones that is't in IK chain
class BoneIKPropsRule(PoseBoneRule):
    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        if bone.is_in_ik_chain:
            return Report.nothing()

        resetted = utils.reset_properties(bone, {
            'ik_linear_weight': None,
            'ik_max_x': 3.1415927410125732,
            'ik_max_y': 3.1415927410125732,
            'ik_max_z': 3.1415927410125732,
            'ik_min_x': -3.1415927410125732,
            'ik_min_y': -3.1415927410125732,
            'ik_min_z': -3.1415927410125732,
            'ik_rotation_weight': None,
            'ik_stiffness_x': None,
            'ik_stiffness_y': None,
            'ik_stiffness_z': None,
            'ik_stretch': None,
            'use_ik_rotation_control': None,
            'use_ik_linear_control': None,
            'use_ik_limit_x': None,
            'use_ik_limit_y': None,
            'use_ik_limit_z': None,
            'lock_ik_x': None,
            'lock_ik_y': None,
            'lock_ik_z': None
        })

        if resetted:
            s = ', '.join(resetted)

            return Report.log(f'Reset "{bone.name}" IK properties: {s}')

        return Report.nothing()


# Do not lock properties except at "CTR" bone
class BoneTransformLockRule(PoseBoneRule):
    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        if re.match('CTR_.*', bone.name):
            return Report.nothing()

        resetted = utils.reset_properties(bone, {
            'lock_location': None,
            'lock_rotation': None,
            'lock_rotations_4d': True,
            'lock_rotation_w': None,
            'lock_scale': None
        })

        if resetted:
            s = ', '.join(resetted)

            return Report.log(f'Reset "{bone.name}" Transform locks: {s}')

        return Report.nothing()


# On pose mode, bone transform must match with rest pose
class RestPoseMatchRule(PoseBoneRule):
    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        ignore = [
            'CTR_thumb_ik.L', 'CTR_finger_index_ik.L', 'CTR_finger_middle_ik.L',
            'CTR_finger_ring_ik.L', 'CTR_finger_pinky_ik.L'
        ]

        if bone.name in ignore or utils.switch_lr(bone.name) in ignore:
            return Report.nothing()

        m = bone.matrix_channel
        m_rest = mathutils.Matrix.Identity(4)
        max_error = 0.0

        for i in range(4):
            for j in range(4):
                error = abs(m[i][j] - m_rest[i][j])

                if error > max_error:
                    max_error = error

        if max_error > 1.0e-3:
            r = Report.error(f'Unmatch with rest pose: {bone.name}')
            r.description = f'error: {max_error}'

            return r

        return Report.nothing()
