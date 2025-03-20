import re
import math
from . import utils
from .rules import ConstraintRule


# Constraint's name rule
class ConstraintNameRule(ConstraintRule):
    @classmethod
    def fix_constraint(cls, constraint, **kwargs):
        constraint_names = {
            'COPY_LOCATION': 'Copy Location',
            'COPY_ROTATION': 'Copy Rotation',
            'COPY_SCALE': 'Copy Scale',
            'COPY_TRANSFORMS': 'Copy Transforms',
            'CHILD_OF': 'Child Of',
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

        if constraint.type not in constraint_names.keys():
            print(f'WARNING: "{constraint.type}" is not supported')

            return False

        name = constraint_names[constraint.type]
        info = []

        m = re.match(r'.*(\s\(|,\s)(X|Y|Z|FK|IK),?.*\)', constraint.name)

        if m:
            info.append(m.group(2))

        if hasattr(constraint, 'target') and constraint.target:
            if constraint.id_data.name != constraint.target.name:
                info.append(constraint.target.name)

        if hasattr(constraint, 'subtarget') and constraint.subtarget:
            info.append(constraint.subtarget)

        if hasattr(constraint, 'influence') and constraint.influence < 1.0:
            if not utils.has_driver(constraint, 'influence'):
                digit = 0

                if constraint.influence > 0.0:
                    digit = math.floor(math.log10(constraint.influence))

                info.append(f'{constraint.influence:.{-digit}f}')

        suffix = ', '.join(info)

        if suffix:
            name += f' ({suffix})'

        if utils.reset_property(constraint, 'name', name):
            print(f'Rename to "{name}"')

            return False

        return True


# Constraint's panel must be shrinked
class ConstraintPanelRule(ConstraintRule):
    @classmethod
    def fix_constraint(cls, constraint, **kwargs):
        if utils.reset_property(constraint, 'show_expanded', False):
            print(f'Shrink "{constraint.name}" constraint panel')

            return False

        return True


# When use bone as subtarget, target space shouldn't use world space
class ConstraintTangetSpaceRule(ConstraintRule):
    @classmethod
    def fix_constraint(cls, constraint, **kwargs):
        notice_types = [
            'COPY_LOCATION', 'COPY_ROTATION', 'COPY_SCALE', 'COPY_TRANSFORMS',
            'LIMIT_DISTANCE', 'TRACK_TO', 'TRANSFORM'
        ]

        ignore_types = [
            'CHILD_OF', 'DAMPED_TRACK', 'LOCKED_TRACK', 'LIMIT_LOCATION',
            'LIMIT_SCALE', 'LIMIT_ROTATION', 'IK', 'SHRINKWRAP', 'STRETCH_TO'
        ]

        if constraint.type in notice_types:
            if constraint.id_data.type != 'ARMATURE':
                return True

            if constraint.target.type != 'ARMATURE':
                return True

            if not constraint.subtarget:
                return True

            if constraint.target_space == 'WORLD':
                print(f'Change "{constraint.name}" target_space to POSE')
                constraint.target_space = 'POSE'

                return False
        elif constraint.type not in ignore_types:
            print(f'WARNING: "{constraint.type}" is not supported')

            return False

        return True


# When use bone constraint, its owner space shouldn't use world space
class ConstraintOwnerSpaceRule(ConstraintRule):
    @classmethod
    def fix_constraint(cls, constraint, **kwargs):
        notice_types = [
            'COPY_LOCATION', 'COPY_ROTATION', 'COPY_SCALE', 'COPY_TRANSFORMS',
            'LIMIT_DISTANCE', 'LIMIT_LOCATION', 'LIMIT_SCALE', 'LIMIT_ROTATION',
            'TRACK_TO', 'TRANSFORM'
        ]

        ignore_types = [
            'CHILD_OF', 'DAMPED_TRACK', 'LOCKED_TRACK',
            'IK', 'SHRINKWRAP', 'STRETCH_TO'
        ]

        if constraint.type in notice_types:
            if constraint.id_data.type != 'ARMATURE':
                return True

            if constraint.owner_space == 'WORLD':
                print(f'Change "{constraint.name}" owner_space to POSE')
                constraint.owner_space = 'POSE'

                return False
        elif constraint.type not in ignore_types:
            print(f'WARNING: "{constraint.type}" is not supported')

            return False

        return True
