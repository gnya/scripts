import bpy
from mathutils import Vector, Matrix
import re


def ik_fk_bone_group(bone):
    m = re.match(r'CTR_(.+)_(ik|fk).+\.(L|R)', bone.name)

    if not m:
        return '', '', ''

    return m.group(1), m.group(2), m.group(3)


def ik_fk_bone_names(group, lr):
    FIRST_BONE_NAME = {
        'arm': 'upperarm',
        'leg': 'thigh'
    }
    SECOND_BONE_NAME = {
        'arm': 'forearm',
        'leg': 'shin'
    }

    if group not in FIRST_BONE_NAME.keys():
        return {}
    if lr not in ['L', 'R']:
        return {}

    first = FIRST_BONE_NAME[group]
    second = SECOND_BONE_NAME[group]

    bone_names = {
        'parent': f'MCH_{group}_parent.{lr}',
        'ik_target': f'CTR_{group}_ik_target.{lr}',
        'ik_pole': f'CTR_{group}_ik_pole.{lr}',
        'ik_length': f'CTR_{group}_ik_length.{lr}',
        'ik_parent': f'MCH_{group}_ik_parent.{lr}',
        'ik_1': f'MCH_{group}_ik_{first}.{lr}',
        'ik_2': f'MCH_{group}_ik_{second}.{lr}',
        'fk_length': f'CTR_{group}_fk_length.{lr}',
        'fk_1': f'CTR_{group}_fk_{first}.{lr}',
        'fk_2': f'CTR_{group}_fk_{second}.{lr}'
    }

    return bone_names


def ik_fk_bones(group, lr):
    obj = bpy.context.active_object
    bones = obj.pose.bones
    bone_names = ik_fk_bone_names(group, lr)

    for v in bone_names.values():
        if v not in bones:
            return None

    ik_fk_bones = {}

    for k, v in bone_names.items():
        ik_fk_bones[k] = bones[v]

    return ik_fk_bones


def set_matrix(bone, location, rotation, scale):
    l, r, s = bone.matrix.decompose()
    l = location if location else l
    r = rotation if rotation else r
    s = scale if scale else s
    bone.matrix = Matrix.LocRotScale(l, r, s)


def project_surface(v, n):
    return v - v.dot(n) / n.dot(n) * n


def snap_fk_to_ik(b):
    # copy scale: ik_length, ik_parent -> fk_length
    s_ik_length = b['ik_length'].matrix.to_scale()
    s_ik_parent = b['ik_parent'].matrix.to_scale()
    s_fk_length = s_ik_length * s_ik_parent
    set_matrix(b['fk_length'], None, None, s_fk_length)

    # copy rotation: ik_1 -> fk_1
    r_ik_1 = b['ik_1'].matrix.to_quaternion()
    s_fk_1 = Vector((1, 1, 1))
    set_matrix(b['fk_1'], None, r_ik_1, s_fk_1)

    # copy rotation: ik_2 -> fk_2
    r_ik_2 = b['ik_2'].matrix.to_quaternion()
    r_ik_2_parent = b['ik_2'].parent.matrix.to_quaternion()
    r_fk_2_parent = b['fk_2'].parent.matrix.to_quaternion()
    r_ik_2_local = r_ik_2_parent.rotation_difference(r_ik_2)
    r_fk_2 = r_fk_2_parent @ r_ik_2_local
    set_matrix(b['fk_2'], None, r_fk_2, None)


def snap_ik_to_fk(b):
    # calc ik_target's location and ik_length's scale
    d_fk = b['fk_2'].tail - b['parent'].head
    c = b['ik_target'].constraints[0]
    l = c.distance
    r = c.influence

    l_fk = d_fk.length
    t = min(l / l_fk, 1.0)
    s = (t + (1 - t) / (1 - r)) if r else 1.0

    # set ik_target
    p_ik_target = s * d_fk + b['parent'].head
    set_matrix(b['ik_target'], p_ik_target, None, None)

    # set ik_length
    s_fk_length = b['fk_length'].matrix.to_scale()
    s_fk_length.y *= t
    set_matrix(b['ik_length'], None, None, s_fk_length)

    # calc ik_pole track
    r_parent = b['parent'].matrix.to_quaternion()
    dir_init = r_parent @ b['ik_parent'].bone.vector
    dir_ik = b['ik_parent'].vector
    dir_fk = d_fk.normalized()

    r_ik_to_init = dir_ik.rotation_difference(dir_init)
    r_init_to_fk = dir_init.rotation_difference(dir_fk)
    r_track = r_init_to_fk @ r_ik_to_init

    d_ik_pole = b['ik_pole'].head - b['parent'].head
    d_ik_pole = r_track @ d_ik_pole

    # calc ik_pole twist
    twist_ik = project_surface(d_ik_pole, dir_fk)
    r_fk_1 = b['fk_1'].matrix.to_quaternion()
    twist_fk = r_fk_1 @ Vector((0, 0, -1))
    twist_fk = project_surface(twist_fk, dir_fk)

    r_twist = twist_ik.rotation_difference(twist_fk)
    d_ik_pole = r_twist @ d_ik_pole

    # cancel damped track constraint
    d_ik_pole = r_track.inverted() @ d_ik_pole

    # set ik_pole
    l_ik_pole = d_ik_pole + b['parent'].head
    set_matrix(b['ik_pole'], l_ik_pole, None, None)


class VIEW3D_OT_rig_snap_ik_to_fk(bpy.types.Operator):
    bl_idname = 'view3d.rig_snap_ik_to_fk'
    bl_label = 'IK → FK'
    bl_description = 'Snap IK to FK'
    bl_options = {'UNDO'}

    bone_group: bpy.props.StringProperty(default='')
    bone_lr: bpy.props.StringProperty(default='')

    def execute(self, context):
        bones = ik_fk_bones(self.bone_group, self.bone_lr)

        if not bones:
            return {'CANCELLED'}

        snap_ik_to_fk(bones)

        return {'FINISHED'}


class VIEW3D_OT_rig_snap_fk_to_ik(bpy.types.Operator):
    bl_idname = 'view3d.rig_snap_fk_to_ik'
    bl_label = 'FK → IK'
    bl_description = 'Snap FK to IK'
    bl_options = {'UNDO'}

    bone_group: bpy.props.StringProperty(default='')
    bone_lr: bpy.props.StringProperty(default='')

    def execute(self, context):
        bones = ik_fk_bones(self.bone_group, self.bone_lr)

        if not bones:
            return {'CANCELLED'}

        snap_fk_to_ik(bones)

        return {'FINISHED'}


class VIEW3D_PT_rig_main(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_main'
    bl_label = 'Rig'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_order = 1

    @classmethod
    def poll(cls, context):
        b = context.active_pose_bone

        if not b:
            return False

        group, _, _ = ik_fk_bone_group(b)

        return group != ''

    def draw(self, context):
        b = context.active_pose_bone
        group = ''
        lr = ''

        if b:
            group, _, lr = ik_fk_bone_group(b)

        if group:
            layout = self.layout
            c = layout.column(align=True)

            c.label(text=f'Snap FK/IK ({group}.{lr})')

            op_ik_fk = c.operator('view3d.rig_snap_ik_to_fk', icon='SNAP_ON')
            op_ik_fk.bone_group = group
            op_ik_fk.bone_lr = lr

            op_fk_ik = c.operator('view3d.rig_snap_fk_to_ik', icon='SNAP_ON')
            op_fk_ik.bone_group = group
            op_fk_ik.bone_lr = lr


bpy.utils.register_class(VIEW3D_OT_rig_snap_ik_to_fk)
bpy.utils.register_class(VIEW3D_OT_rig_snap_fk_to_ik)
bpy.utils.register_class(VIEW3D_PT_rig_main)
