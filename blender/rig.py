import bpy
from mathutils import Vector, Matrix
import re


def check_ik_fk_bone(bone):
    name = bone.name if bone else ''
    match = re.match(r'CTR_(.+)_(ik|fk).*\.(L|R)', name)

    if not match:
        return False, '', '', ''

    group = match.group(1)
    ik_or_fk = match.group(2)
    l_or_r = match.group(3)

    if group not in ['arm', 'leg']:
        if group in ['hand']:
            group = 'arm'
        elif group in ['foot', 'toe', 'heel', 'foot_spin']:
            group = 'leg'
        else:
            group = ''

    if ik_or_fk not in ['ik', 'fk']:
        ik_or_fk = ''

    if l_or_r not in ['L', 'R']:
        l_or_r = ''

    if group and ik_or_fk and l_or_r:
        return True, group, ik_or_fk, l_or_r

    return False, '', '', ''


def ik_fk_arm_bone_names(lr):
    return {
        'parent': f'MCH_arm_parent.{lr}',
        'ik_pole': f'CTR_arm_ik_pole.{lr}',
        'ik_length': f'CTR_arm_ik_length.{lr}',
        'ik_parent': f'MCH_arm_ik_parent.{lr}',
        'ik_target': f'MCH_arm_ik_target.{lr}',
        'ik_1': f'MCH_arm_ik_upperarm.{lr}',
        'ik_2': f'MCH_arm_ik_forearm.{lr}',
        'ik_3': f'CTR_hand_ik.{lr}',
        'fk_length': f'CTR_arm_fk_length.{lr}',
        'fk_1': f'CTR_arm_fk_upperarm.{lr}',
        'fk_2': f'CTR_arm_fk_forearm.{lr}',
        'fk_3': f'CTR_hand_fk.{lr}'
    }


def ik_fk_leg_bone_names(lr):
    return {
        'parent': f'MCH_leg_parent.{lr}',
        'ik_pole': f'CTR_leg_ik_pole.{lr}',
        'ik_length': f'CTR_leg_ik_length.{lr}',
        'ik_parent': f'MCH_leg_ik_parent.{lr}',
        'ik_target': f'MCH_leg_ik_target.{lr}',
        'ik_1': f'MCH_leg_ik_thigh.{lr}',
        'ik_2': f'MCH_leg_ik_shin.{lr}',
        'ik_3': f'CTR_foot_ik.{lr}',
        'ik_3_dash': f'MCH_foot_ik.{lr}',
        'ik_4': f'CTR_toe_ik.{lr}',
        'ik_4_parent': f'MCH_toe_ik.{lr}',
        'ik_heel': f'CTR_heel_ik.{lr}',
        'ik_foot_spin': f'CTR_foot_spin_ik.{lr}',
        'fk_length': f'CTR_leg_fk_length.{lr}',
        'fk_1': f'CTR_leg_fk_thigh.{lr}',
        'fk_2': f'CTR_leg_fk_shin.{lr}',
        'fk_3': f'CTR_foot_fk.{lr}',
        'fk_4': f'CTR_toe_fk.{lr}',
        'fk_4_parent': f'MCH_toe_fk.{lr}'
    }


def ik_fk_bones(group, lr):
    bone_names = {}

    if 'arm' == group:
        bone_names = ik_fk_arm_bone_names(lr)
    elif 'leg' == group:
        bone_names = ik_fk_leg_bone_names(lr)

    obj = bpy.context.active_object
    bones = obj.pose.bones

    ik_fk_bones = {}
    missing_bones = {}

    for k, v in bone_names.items():
        if v in bones:
            ik_fk_bones[k] = bones[v]
        else:
            missing_bones[k] = v

    return ik_fk_bones, missing_bones


def set_matrix(bone, location, rotation, scale):
    l, r, s = bone.matrix.decompose()
    l = location if location else l
    r = rotation if rotation else r
    s = scale if scale else s
    bone.matrix = Matrix.LocRotScale(l, r, s)


def get_rotation_local(bone, parent=None):
    parent = parent if parent else bone.parent

    r_parent = parent.matrix.to_quaternion()
    r = bone.matrix.to_quaternion()

    return r_parent.inverted() @ r


def project_surface(v, n):
    return v - v.dot(n) / n.dot(n) * n


def set_fk_length(fk_length, ik_length, ik_parent):
    s_ik_length = ik_length.matrix.to_scale()
    s_ik_parent = ik_parent.matrix.to_scale()
    s_fk_length = s_ik_length * s_ik_parent
    set_matrix(fk_length, None, None, s_fk_length)


def set_fk_1(fk_1, ik_1):
    r_ik_1 = ik_1.matrix.to_quaternion()
    set_matrix(fk_1, None, r_ik_1, Vector((1, 1, 1)))


def set_fk_2(fk_2, fk_1, ik_2):
    r_fk_1 = fk_1.matrix.to_quaternion()
    r_ik_2_local = get_rotation_local(ik_2)
    r_fk_2 = r_fk_1 @ r_ik_2_local
    set_matrix(fk_2, None, r_fk_2, None)


def set_fk_3(fk_3, fk_2, ik_3, ik_2):
    r_fk_2 = fk_2.matrix.to_quaternion()
    r_ik_3_local = get_rotation_local(ik_3, parent=ik_2)
    r_fk_3 = r_fk_2 @ r_ik_3_local
    s_ik_3 = ik_3.matrix.to_scale()
    set_matrix(fk_3, None, r_fk_3, s_ik_3)


def set_fk_4(fk_4, fk_3, ik_4, ik_3):
    m_ik_4_local = ik_3.matrix.inverted() @ ik_4.matrix
    fk_4.matrix = fk_3.matrix @ m_ik_4_local


def snap_arm_fk2ik(b):
    set_fk_length(b['fk_length'], b['ik_length'], b['ik_parent'])
    set_fk_1(b['fk_1'], b['ik_1'])
    set_fk_2(b['fk_2'], b['fk_1'], b['ik_2'])
    set_fk_3(b['fk_3'], b['fk_2'], b['ik_3'], b['ik_2'])


def snap_leg_fk2ik(b):
    set_fk_length(b['fk_length'], b['ik_length'], b['ik_parent'])
    set_fk_1(b['fk_1'], b['ik_1'])
    set_fk_2(b['fk_2'], b['fk_1'], b['ik_2'])
    set_fk_3(b['fk_3'], b['fk_2'], b['ik_3_dash'], b['ik_2'])
    set_fk_4(b['fk_4'], b['fk_3'], b['ik_4'], b['ik_3_dash'])


def set_ik_3(ik_3, fk_3, parent, ik_target, d_fk):
    c = ik_target.constraints[0]
    r = c.influence
    t = min(c.distance / d_fk.length, 1.0)
    s = (t + (1 - t) / (1 - r)) if r else 1.0

    _, r_fk_3, s_fk_3 = fk_3.matrix.decompose()
    l_ik_3 = s * d_fk + parent.head
    set_matrix(ik_3, l_ik_3, r_fk_3, s_fk_3)


def set_ik_length(ik_length, fk_length, ik_target, d_fk):
    c = ik_target.constraints[0]
    t = min(c.distance / d_fk.length, 1.0)

    s_fk_length = fk_length.matrix.to_scale()
    s_fk_length.y *= t
    set_matrix(ik_length, None, None, s_fk_length)


def set_ik_pole(ik_pole, parent, ik_parent, fk_1, d_fk):
    # calc ik_pole track
    r_parent = parent.matrix.to_quaternion()
    dir_init = r_parent @ ik_parent.bone.vector
    dir_ik = ik_parent.vector
    dir_fk = d_fk.normalized()

    r_ik_to_init = dir_ik.rotation_difference(dir_init)
    r_init_to_fk = dir_init.rotation_difference(dir_fk)
    r_track = r_init_to_fk @ r_ik_to_init

    d_ik_pole = ik_pole.head - parent.head
    d_ik_pole = r_track @ d_ik_pole

    # calc ik_pole twist
    twist_ik = project_surface(d_ik_pole, dir_fk)
    r_fk_1 = fk_1.matrix.to_quaternion()
    twist_fk = r_fk_1 @ Vector((0, 0, -1))
    twist_fk = project_surface(twist_fk, dir_fk)

    r_twist = twist_ik.rotation_difference(twist_fk)
    d_ik_pole = r_twist @ d_ik_pole

    # cancel damped track constraint
    d_ik_pole = r_track.inverted() @ d_ik_pole

    # set location: ik_pole
    l_ik_pole = d_ik_pole + parent.head
    set_matrix(ik_pole, l_ik_pole, None, None)


def reset_pose(bone):
    bone.matrix_basis = Matrix.Identity(4)


def set_ik_4(ik_4, ik_4_parent, fk_4, fk_4_parent):
    m_fk_4_local = fk_4_parent.matrix.inverted() @ fk_4.matrix
    ik_4.matrix = ik_4_parent.matrix @ m_fk_4_local


def snap_arm_ik2fk(b):
    d_fk = b['fk_2'].tail - b['parent'].head

    set_ik_3(b['ik_3'], b['fk_3'], b['parent'], b['ik_target'], d_fk)
    set_ik_length(b['ik_length'], b['fk_length'], b['ik_target'], d_fk)
    set_ik_pole(b['ik_pole'], b['parent'], b['ik_parent'], b['fk_1'], d_fk)


def snap_leg_ik2fk(b):
    d_fk = b['fk_2'].tail - b['parent'].head

    reset_pose(b['ik_foot_spin'])
    reset_pose(b['ik_heel'])
    set_ik_3(b['ik_3'], b['fk_3'], b['parent'], b['ik_target'], d_fk)
    set_ik_length(b['ik_length'], b['fk_length'], b['ik_target'], d_fk)
    set_ik_pole(b['ik_pole'], b['parent'], b['ik_parent'], b['fk_1'], d_fk)
    set_ik_4(b['ik_4'], b['ik_4_parent'], b['fk_4'], b['fk_4_parent'])


class VIEW3D_OT_rig_snap_ik_to_fk(bpy.types.Operator):
    bl_idname = 'view3d.rig_snap_ik_to_fk'
    bl_label = 'IK → FK'
    bl_description = 'Snap IK to FK'
    bl_options = {'UNDO'}

    bone_group: bpy.props.StringProperty(default='')
    bone_lr: bpy.props.StringProperty(default='')

    def execute(self, _):
        bones, missing = ik_fk_bones(self.bone_group, self.bone_lr)

        if not bones:
            self.report({'ERROR'}, 'Required ik/fk bones not found.')

            return {'CANCELLED'}
        elif missing:
            self.report({'ERROR'}, f'Required ik/fk bones are missing. : {missing}')

            return {'CANCELLED'}

        if self.bone_group == 'arm':
            snap_arm_ik2fk(bones)
        elif self.bone_group == 'leg':
            snap_leg_ik2fk(bones)

        return {'FINISHED'}


class VIEW3D_OT_rig_snap_fk_to_ik(bpy.types.Operator):
    bl_idname = 'view3d.rig_snap_fk_to_ik'
    bl_label = 'FK → IK'
    bl_description = 'Snap FK to IK'
    bl_options = {'UNDO'}

    bone_group: bpy.props.StringProperty(default='')
    bone_lr: bpy.props.StringProperty(default='')

    def execute(self, _):
        bones, missing = ik_fk_bones(self.bone_group, self.bone_lr)

        if not bones:
            self.report({'ERROR'}, 'Required ik/fk bones not found.')

            return {'CANCELLED'}
        elif missing:
            self.report({'ERROR'}, f'Required ik/fk bones are missing. : {missing}')

            return {'CANCELLED'}

        if self.bone_group == 'arm':
            snap_arm_fk2ik(bones)
        elif self.bone_group == 'leg':
            snap_leg_fk2ik(bones)

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
        check, _, _, _ = check_ik_fk_bone(b)

        return check

    def draw(self, context):
        b = context.active_pose_bone
        check, group, _, lr = check_ik_fk_bone(b)

        if check:
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
