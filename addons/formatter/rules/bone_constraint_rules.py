import re
import math
from . import utils
from .rules import BoneConstraintRule


# Armature target must have subtarget
# and use "Pose Space" instead of "World Space"
class BoneConstraintTangetSpaceRule(BoneConstraintRule):
    @classmethod
    def fix_bone_constraint(cls, _, bone, constraint):
        notice_types = [
            'COPY_LOCATION', 'COPY_ROTATION', 'COPY_SCALE', 'COPY_TRANSFORMS',
            'LIMIT_DISTANCE', 'TRACK_TO', 'TRANSFORM'
        ]

        ignore_types = [
            'DAMPED_TRACK', 'LOCKED_TRACK', 'LIMIT_LOCATION', 'LIMIT_SCALE',
            'LIMIT_ROTATION', 'IK', 'SHRINKWRAP', 'STRETCH_TO'
        ]

        if constraint.type in notice_types:
            if constraint.target.type != 'ARMATURE':
                return True

            if not constraint.subtarget:
                print(f'WARNING: "{constraint.name}" doesn\'t have subtarget')

                return False

            if constraint.target_space == 'WORLD':
                print(f'Change "{constraint.name}" target_space to Pose')
                constraint.target_space = 'POSE'

                return False
        elif constraint.type not in ignore_types:
            print(f'WARNING: "{constraint.type}" is not supported')

            return False

        return True


# Owner must use "Pose Space" instead of "World Space"
class BoneConstraintOwnerSpaceRule(BoneConstraintRule):
    @classmethod
    def fix_bone_constraint(cls, _, bone, constraint):
        notice_types = [
            'COPY_LOCATION', 'COPY_ROTATION', 'COPY_SCALE', 'COPY_TRANSFORMS',
            'LIMIT_DISTANCE', 'LIMIT_LOCATION', 'LIMIT_SCALE', 'LIMIT_ROTATION',
            'TRACK_TO', 'TRANSFORM'
        ]

        ignore_types = [
            'DAMPED_TRACK', 'LOCKED_TRACK', 'IK', 'SHRINKWRAP', 'STRETCH_TO'
        ]

        if constraint.type in notice_types:
            if constraint.owner_space == 'WORLD':
                print(f'Change "{constraint.name}" owner_space to Pose')
                constraint.owner_space = 'POSE'

                return False
        elif constraint.type not in ignore_types:
            print(f'WARNING: "{constraint.type}" is not supported')

            return False

        return True


# Armature target must have subtarget
class BoneConstraintSubtangentRule(BoneConstraintRule):
    @classmethod
    def fix_bone_constraint(cls, _, bone, constraint):
        notice_types = [
            'COPY_LOCATION', 'COPY_ROTATION', 'COPY_SCALE', 'COPY_TRANSFORMS',
            'DAMPED_TRACK', 'LOCKED_TRACK',
            'IK', 'LIMIT_DISTANCE', 'STRETCH_TO', 'TRACK_TO', 'TRANSFORM'
        ]

        ignore_types = [
            'LIMIT_LOCATION', 'LIMIT_SCALE', 'LIMIT_ROTATION', 'SHRINKWRAP'
        ]

        if constraint.type in notice_types:
            if constraint.target.type != 'ARMATURE':
                return True

            if not constraint.subtarget:
                print(f'WARNING: "{constraint.name}" doesn\'t have subtarget')

                return False
        elif constraint.type not in ignore_types:
            print(f'WARNING: "{constraint.type}" is not supported')

            return False

        return True


# Constraint's name rule
class BoneConstraintNameRule(BoneConstraintRule):
    @classmethod
    def fix_bone_constraint(cls, armature, bone, constraint):
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
                if not utils.has_driver(armature, bone, constraint, 'influence'):
                    digit = 0

                    if constraint.influence > 0.0:
                        digit = math.floor(math.log10(constraint.influence))

                    info.append(f'{constraint.influence:.{-digit}f}')

            suffix = ', '.join(info)

            if suffix:
                name += f' ({suffix})'

            if name != constraint.name:
                print(f'Rename "{constraint.name}" to "{name}"')
                constraint.name = name

                return False
        else:
            print(f'WARNING: "{constraint.type}" is not supported')

            return False

        return True


# Constraint's panel must be shrinked
class BoneConstraintPanelRule(BoneConstraintRule):
    @classmethod
    def fix_bone_constraint(cls, _, bone, constraint):
        if constraint.show_expanded:
            print(f'Shrink "{bone.name}" constraint panel')
            constraint.show_expanded = False

            return False

        return True
