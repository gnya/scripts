import bpy
from . import utils


class Report():
    def __init__(self, title, description='', type='NONE'):
        self.type = type
        self.title = title
        self.description = description
        self.children = []

    def to_list(self, type):
        reports = []

        if self.type == type:
            reports.append(self)

        for r in self.children:
            reports += r.to_list(type)

        return reports

    @staticmethod
    def nothing(title='', description=''):
        return Report(title, description)

    @staticmethod
    def log(title, description=''):
        return Report(title, description, type='LOG')

    @staticmethod
    def error(title, description=''):
        return Report(title, description, type='ERROR')


class Rule():
    @classmethod
    def fix(cls, **kwargs):
        raise NotImplementedError()


class ObjectRule(Rule):
    @classmethod
    def fix_object(cls, obj, **kwargs):
        raise NotImplementedError()

    @classmethod
    def local_objects(cls):
        for o in bpy.data.objects:
            if not (o.library or o.override_library):
                yield o

    @classmethod
    def fix(cls, **kwargs):
        r = Report.nothing()

        for o in cls.local_objects():
            r.children.append(cls.fix_object(o, **kwargs))

        return r


class SceneRule(Rule):
    @classmethod
    def fix_scene(cls, scene, **kwargs):
        raise NotImplementedError()

    @classmethod
    def fix(cls, **kwargs):
        r = Report.nothing()

        for s in bpy.data.scenes:
            r.children.append(cls.fix_scene(s, **kwargs))

        return r


class NodeTreeRule(Rule):
    @classmethod
    def fix_node_tree(cls, node_tree, **kwargs):
        raise NotImplementedError()

    @classmethod
    def fix(cls, **kwargs):
        r = Report.nothing()

        for t in bpy.data.scenes:
            if t.node_tree:
                r.children.append(cls.fix_node_tree(t.node_tree, scene=t, name=t.name, **kwargs))

        for t in bpy.data.worlds:
            if t.node_tree:
                r.children.append(cls.fix_node_tree(t.node_tree, world=t, name=t.name, **kwargs))

        for t in bpy.data.materials:
            if t.node_tree:
                r.children.append(cls.fix_node_tree(t.node_tree, material=t, name=t.name, **kwargs))

        for t in bpy.data.linestyles:
            if t.node_tree:
                r.children.append(cls.fix_node_tree(t.node_tree, linestyle=t, name=t.name, **kwargs))

        for t in bpy.data.node_groups:
            r.children.append(cls.fix_node_tree(t, name=t.name, **kwargs))

        return r


class MeshRule(ObjectRule):
    @classmethod
    def fix_mesh(cls, mesh, **kwargs):
        raise NotImplementedError()

    @classmethod
    def fix_object(cls, obj, **kwargs):
        if obj.type == 'MESH':
            return cls.fix_mesh(obj)

        return Report.nothing()


class ArmatureRule(ObjectRule):
    @classmethod
    def fix_armature(cls, armature, **kwargs):
        raise NotImplementedError()

    @classmethod
    def fix_object(cls, obj, **kwargs):
        if obj.type == 'ARMATURE':
            return cls.fix_armature(obj, **kwargs)

        return Report.nothing()


class ModifierRule(ObjectRule):
    @classmethod
    def fix_modifier(cls, modifier, **kwargs):
        raise NotImplementedError()

    @classmethod
    def fix_object(cls, obj, **kwargs):
        r = Report.nothing()

        for m in obj.modifiers:
            r.children.append(cls.fix_modifier(m, obj=obj, **kwargs))

        return r


class BoneDriverRule(ArmatureRule):
    @classmethod
    def fix_bone_driver(cls, driver, **kwargs):
        raise NotImplementedError()

    @classmethod
    def fix_armature(cls, armature, **kwargs):
        if not armature.animation_data:
            return Report.nothing()

        r = Report.nothing()
        drivers = armature.animation_data.drivers

        for d in drivers:
            r.children.append(cls.fix_bone_driver(d, drivers=drivers, **kwargs))

        return r


class DataBoneRule(ArmatureRule):
    @classmethod
    def fix_data_bone(cls, bone, **kwargs):
        raise NotImplementedError()

    @classmethod
    def fix_armature(cls, armature, **kwargs):
        r = Report.nothing()

        for b in armature.data.bones:
            r.children.append(cls.fix_data_bone(b, armature=armature, **kwargs))

        return r


class PoseBoneRule(ArmatureRule):
    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        raise NotImplementedError()

    @classmethod
    def fix_armature(cls, armature, **kwargs):
        r = Report.nothing()

        for b in armature.pose.bones:
            r.children.append(cls.fix_pose_bone(b, armature=armature, **kwargs))

        return r


class SymmetryBoneRule(PoseBoneRule):
    @classmethod
    def fix_symmetry_bone(cls, bone, pair_bone, **kwargs):
        raise NotImplementedError()

    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        armature = kwargs['armature']
        pair_bone_name = utils.switch_lr(bone.name)
        pair_bone = armature.pose.bones.get(pair_bone_name)

        return cls.fix_symmetry_bone(bone, pair_bone, **kwargs)


class BoneConstraintRule(PoseBoneRule):
    @classmethod
    def fix_bone_constraint(cls, constraint, **kwargs):
        raise NotImplementedError()

    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        r = Report.nothing()

        for c in bone.constraints:
            r.children.append(cls.fix_bone_constraint(c, bone=bone, **kwargs))

        return r


class ConstraintRule(PoseBoneRule):
    @classmethod
    def fix_constraint(cls, constraint, **kwargs):
        raise NotImplementedError()

    @classmethod
    def fix_pose_bone(cls, bone, **kwargs):
        r = Report.nothing()

        for c in bone.constraints:
            r.children.append(cls.fix_constraint(c, bone=bone, **kwargs))

        return r

    @classmethod
    def fix_object(cls, obj, **kwargs):
        r = super(PoseBoneRule, cls).fix_object(obj, **kwargs)

        for c in obj.constraints:
            r.children.append(cls.fix_constraint(c, obj=obj, **kwargs))

        return r
