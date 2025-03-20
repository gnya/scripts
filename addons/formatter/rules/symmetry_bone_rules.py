from . import utils
from .rules import Report, SymmetryBoneRule


# Check bone is symmetrical
class SymmetryBoneNameRule(SymmetryBoneRule):
    @classmethod
    def fix_symmetry_bone(cls, bone, symmetry_bone, **kwargs):
        if not symmetry_bone:
            return Report.error(f'"{bone.name}" doesn\'t have pair bone')

        return Report.nothing()


# Check bone parent is symmetrical
class SymmetryBoneParentRule(SymmetryBoneRule):
    @classmethod
    def fix_symmetry_bone(cls, bone, pair_bone, **kwargs):
        if not pair_bone:
            return Report.nothing()

        if not bone.parent:
            return Report.nothing()

        parent_name = bone.parent.name
        pair_parent_name = utils.switch_lr(pair_bone.parent.name)

        if not pair_bone.parent or parent_name != pair_parent_name:
            return Report.error(f'"{bone.name}" doesn\'t have pair parent')

        return Report.nothing()


# Check bone constraint is symmetrical
class SymmetryBoneConstraintRule(SymmetryBoneRule):
    @classmethod
    def fix_symmetry_bone(cls, bone, pair_bone, **kwargs):
        if not pair_bone:
            return Report.nothing()

        if len(bone.constraints) != len(pair_bone.constraints):
            return Report.error(f'"{bone.name}" doesn\'t have pair constraints')

        for (a_c, b_c) in zip(bone.constraints, pair_bone.constraints):
            is_pair, s = utils.is_symmetrical_constraint(a_c, b_c)

            if not is_pair:
                return Report.error(f'"{a_c.name}" is not symmetrical: {s}')

        return Report.nothing()
