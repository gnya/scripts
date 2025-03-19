import re
from . import utils
from .rules import PoseBoneRule


# Check IK properties in bones that is't in IK chain
class BoneIKPropsRule(PoseBoneRule):
    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        if bone.is_in_ik_chain:
            return True

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
            print(f'Reset "{bone.name}" IK properties: {s}')

            return False

        return True


# Do not lock properties except at "CTR" bone
class BoneTransformLockRule(PoseBoneRule):
    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        if re.match('CTR_.*', bone.name):
            return True

        resetted = utils.reset_properties(bone, {
            'lock_location': None,
            'lock_rotation': None,
            'lock_rotations_4d': True,
            'lock_rotation_w': None,
            'lock_scale': None
        })

        if resetted:
            s = ', '.join(resetted)
            print(f'Reset "{bone.name}" Transform locks: {s}')

            return False

        return True
