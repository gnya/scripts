import bpy
from . import utils


class Rule():
    @classmethod
    def fix(cls):
        raise Exception('Not Implemented')


class ArmaturesRule(Rule):
    @classmethod
    def fix_armatures(cls, armatures):
        raise Exception('Not Implemented')

    @classmethod
    def fix(cls):
        armatures = []

        for o in bpy.context.selected_objects:
            if o.type == 'ARMATURE':
                armatures.append(o)

        return cls.fix_armatures(armatures)


class ArmatureRule(ArmaturesRule):
    @classmethod
    def fix_armature(cls, armature):
        raise Exception('Not Implemented')

    @classmethod
    def fix_armatures(cls, armatures):
        result = True

        for a in armatures:
            if not cls.fix_armature(a):
                result = False

        return result


class DataBoneRule(ArmatureRule):
    @classmethod
    def fix_data_bone(cls, armature, bone):
        raise Exception('Not Implemented')

    @classmethod
    def fix_armature(cls, armature):
        result = True

        for b in armature.data.bones:
            if not cls.fix_data_bone(armature, b):
                result = False

        return result


class PoseBoneRule(ArmatureRule):
    @classmethod
    def fix_pose_bone(cls, armature, bone):
        raise Exception('Not Implemented')

    @classmethod
    def fix_armature(cls, armature):
        result = True

        for b in armature.pose.bones:
            if not cls.fix_pose_bone(armature, b):
                result = False

        return result


class SymmetryBoneRule(PoseBoneRule):
    @classmethod
    def fix_symmetry_bone(cls, armature, bone, symmetry_bone):
        raise Exception('Not Implemented')

    @classmethod
    def fix_pose_bone(cls, armature, bone):
        symmetry_bone_name = utils.switch_lr(bone.name)
        symmetry_bone = armature.pose.bones.get(symmetry_bone_name)

        return cls.fix_symmetry_bone(armature, bone, symmetry_bone)


class BoneConstraintRule(PoseBoneRule):
    @classmethod
    def fix_bone_constraint(cls, armature, bone, constraint):
        raise Exception('Not Implemented')

    @classmethod
    def fix_pose_bone(cls, armature, bone):
        result = True

        for c in bone.constraints:
            if not cls.fix_bone_constraint(armature, bone, c):
                result = False

        return result


class BoneDriverRule(ArmatureRule):
    @classmethod
    def fix_bone_driver(cls, drivers, driver):
        raise Exception('Not Implemented')

    @classmethod
    def fix_armature(cls, armature):
        if not armature.animation_data:
            return True

        result = True
        drivers = armature.animation_data.drivers

        for d in drivers:
            if not cls.fix_bone_driver(drivers, d):
                result = False

        return result


class ModifierRule(ArmatureRule):
    @classmethod
    def fix_modifier(cls, obj, modifier):
        raise Exception('Not Implemented')

    @classmethod
    def fix_armature(cls, armature):
        result = True

        for c in armature.children_recursive:
            for m in c.modifiers:
                if not cls.fix_modifier(c, m):
                    result = False

        return result
