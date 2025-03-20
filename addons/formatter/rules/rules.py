import bpy
from . import utils


class Report():
    def __init__(self, logs, errors):
        self.logs = logs
        self.errors = errors

    def add(self, report):
        self.logs.extend(report.logs)
        self.errors.extend(report.errors)

    @staticmethod
    def nothing():
        return Report([], [])

    @staticmethod
    def log(log):
        return Report([log], [])

    @staticmethod
    def error(error):
        return Report([], [error])


class Rule():
    @classmethod
    def fix(cls, **kwargs):
        raise Exception('Not Implemented')


class ObjectRule(Rule):
    @classmethod
    def fix_object(cls, obj, **kwargs):
        raise Exception('Not Implemented')

    @classmethod
    def fix(cls, **kwargs):
        r = Report.nothing()

        for o in bpy.data.objects:
            r.add(cls.fix_object(o, **kwargs))

        return r


class ScenePropertiesRule(Rule):
    @classmethod
    def fix_scene_properties(cls, scene, **kwargs):
        raise Exception('Not Implemented')

    @classmethod
    def fix(cls, **kwargs):
        r = Report.nothing()

        for s in bpy.data.scenes:
            r.add(cls.fix_scene_properties(s, **kwargs))

        return r


class ArmatureRule(ObjectRule):
    @classmethod
    def fix_armature(cls, armature, **kwargs):
        raise Exception('Not Implemented')

    @classmethod
    def fix_object(cls, obj, **kwargs):
        if obj.type == 'ARMATURE':
            return cls.fix_armature(obj, **kwargs)

        return Report.nothing()


class ModifierRule(ObjectRule):
    @classmethod
    def fix_modifier(cls, modifier, **kwargs):
        raise Exception('Not Implemented')

    @classmethod
    def fix_object(cls, obj, **kwargs):
        r = Report.nothing()

        for m in obj.modifiers:
            r.add(cls.fix_modifier(m, obj=obj, **kwargs))

        return r


class BoneDriverRule(ArmatureRule):
    @classmethod
    def fix_bone_driver(cls, driver, **kwargs):
        raise Exception('Not Implemented')

    @classmethod
    def fix_armature(cls, armature, **kwargs):
        if not armature.animation_data:
            return Report.nothing()

        r = Report.nothing()
        drivers = armature.animation_data.drivers

        for d in drivers:
            r.add(cls.fix_bone_driver(d, drivers=drivers, **kwargs))

        return r


class DataBoneRule(ArmatureRule):
    @classmethod
    def fix_data_bone(cls, bone, **kwargs):
        raise Exception('Not Implemented')

    @classmethod
    def fix_armature(cls, armature, **kwargs):
        r = Report.nothing()

        for b in armature.data.bones:
            r.add(cls.fix_data_bone(b, armature=armature, **kwargs))

        return r


class PoseBoneRule(ArmatureRule):
    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        raise Exception('Not Implemented')

    @classmethod
    def fix_armature(cls, armature, **kwargs):
        r = Report.nothing()

        for b in armature.pose.bones:
            r.add(cls.fix_pose_bone(b, armature=armature, **kwargs))

        return r


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
        r = Report.nothing()

        for c in bone.constraints:
            r.add(cls.fix_bone_constraint(c, bone=bone, **kwargs))

        return r


class ConstraintRule(PoseBoneRule):
    @classmethod
    def fix_constraint(cls, constraint, **kwargs):
        raise Exception('Not Implemented')

    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        r = Report.nothing()

        for c in bone.constraints:
            r.add(cls.fix_constraint(c, bone=bone, **kwargs))

        return r

    @classmethod
    def fix_object(cls, obj, **kwargs):
        r = super(PoseBoneRule, cls).fix_object(obj, **kwargs)

        for c in obj.constraints:
            r.add(cls.fix_constraint(c, obj=obj, **kwargs))

        return r
