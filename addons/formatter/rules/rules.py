import bpy
from . import utils


class Rule():
    @classmethod
    def fix(cls):
        raise Exception('Not Implemented')


class ObjectRule(Rule):
    @classmethod
    def fix_object(cls, obj):
        raise Exception('Not Implemented')

    @classmethod
    def fix(cls):
        result = True

        for o in bpy.data.objects:
            if not cls.fix_object(o):
                result = False

        return result


class ArmatureRule(ObjectRule):
    @classmethod
    def fix_armature(cls, armature):
        raise Exception('Not Implemented')

    @classmethod
    def fix_object(cls, obj):
        if obj.type == 'ARMATURE':
            return cls.fix_armature(obj)

        return True


class ModifierRule(ObjectRule):
    @classmethod
    def fix_modifier(cls, modifier, **kwargs):
        raise Exception('Not Implemented')

    @classmethod
    def fix_object(cls, obj):
        result = True

        for m in obj.modifiers:
            if not cls.fix_modifier(m, obj=obj):
                result = False

        return result


class DataBoneRule(ArmatureRule):
    @classmethod
    def fix_data_bone(cls, bone, **kwargs):
        raise Exception('Not Implemented')

    @classmethod
    def fix_armature(cls, armature):
        result = True

        for b in armature.data.bones:
            if not cls.fix_data_bone(b, armature=armature):
                result = False

        return result


class PoseBoneRule(ArmatureRule):
    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        raise Exception('Not Implemented')

    @classmethod
    def fix_armature(cls, armature):
        result = True

        for b in armature.pose.bones:
            if not cls.fix_pose_bone(b, armature=armature):
                result = False

        return result


class SymmetryBoneRule(PoseBoneRule):
    @classmethod
    def fix_symmetry_bone(cls, bone, pair_bone, **kwargs):
        raise Exception('Not Implemented')

    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        armature = kwargs['armature']
        pair_bone_name = utils.switch_lr(bone.name)
        pair_bone = armature.pose.bones.get(pair_bone_name)

        return cls.fix_symmetry_bone(bone, pair_bone, **kwargs)


class BoneConstraintRule(PoseBoneRule):
    @classmethod
    def fix_bone_constraint(cls, constraint, **kwargs):
        raise Exception('Not Implemented')

    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        result = True

        for c in bone.constraints:
            if not cls.fix_bone_constraint(c, bone=bone, **kwargs):
                result = False

        return result


class ConstraintRule(PoseBoneRule):
    @classmethod
    def fix_constraint(cls, constraint, **kwargs):
        raise Exception('Not Implemented')

    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        result = True

        for c in bone.constraints:
            if not cls.fix_constraint(c, bone=bone, **kwargs):
                result = False

        return result

    @classmethod
    def fix_object(cls, obj):
        result = super(PoseBoneRule, cls).fix_object(obj)

        for c in obj.constraints:
            if not cls.fix_constraint(c, obj=obj):
                result = False

        return result


class BoneDriverRule(ArmatureRule):
    @classmethod
    def fix_bone_driver(cls, driver, **kwargs):
        raise Exception('Not Implemented')

    @classmethod
    def fix_armature(cls, armature):
        if not armature.animation_data:
            return True

        result = True
        drivers = armature.animation_data.drivers

        for d in drivers:
            if not cls.fix_bone_driver(d, drivers=drivers):
                result = False

        return result
