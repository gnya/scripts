from . import utils
from .rules import SymmetryBoneRule


# Check bone is symmetrical
class SymmetryBoneNameRule(SymmetryBoneRule):
    @classmethod
    def fix_symmetry_bone(cls, _, bone, symmetry_bone):
        if not symmetry_bone:
            print(f'WARNING: "{bone.name}" doesn\'t have pair bone')

            return False

        return True


# Check bone constraint is symmetrical
class SymmetryBoneConstraintRule(SymmetryBoneRule):
    @classmethod
    def fix_symmetry_bone(cls, _, bone, symmetry_bone):
        if len(bone.constraints) != len(symmetry_bone.constraints):
            print(f'WARNING: "{bone.name}" doesn\'t have pair constraints')

            return False

        for (a_c, b_c) in zip(bone.constraints, symmetry_bone.constraints):
            is_mirror, s = utils.is_symmetrical_constraint(a_c, b_c)

            if not is_mirror:
                print(f'WARNING: "{a_c.name}" is not symmetrical: {s}')

                return False

        return True


# Check bone parent is symmetrical
class SymmetryBoneParentRule(SymmetryBoneRule):
    @classmethod
    def fix_symmetry_bone(cls, _, bone, symmetry_bone):
        if not bone.parent:
            return True

        parent_name = bone.parent.name
        mirror_parent_name = utils.switch_lr(symmetry_bone.parent.name)

        if not symmetry_bone.parent or parent_name != mirror_parent_name:
            print(f'WARNING: "{bone.name}" doesn\'t have pair parent')

            return False

        return True
