import re
from . import utils
from .rules import PoseBoneRule


# Check IK properties in bones that is't in IK chain
class BoneIKPropsRule(PoseBoneRule):
    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        if not bone.is_in_ik_chain:
            is_default, s = utils.reset_properties(bone, [
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
                print(f'Reset "{bone.name}" IK properties: {s}')

                return False

        return True


# Do not lock properties except at "CTR" bone
class BoneTransformLockRule(PoseBoneRule):
    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        if not re.match('CTR_.*', bone.name):
            is_default, s = utils.reset_properties(bone, [
                'lock_location', 'lock_rotation',
                'lock_rotations_4d', 'lock_rotation_w', 'lock_scale'
            ], {
                'lock_rotations_4d': True
            })

            if not is_default:
                print(f'Reset "{bone.name}" Transform locks: {s}')

                return False

        return True
