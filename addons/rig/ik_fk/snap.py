from mathutils import Vector, Matrix


def set_matrix(bone, location, rotation, scale):
    l, r, s = bone.matrix.decompose()
    l = location if location else l  # noqa: E741
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


def set_ik_pole(ik_pole, ik_pole_parent, parent, ik_parent, fk_1, d_fk):
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

    # calc ik_pole following
    c = ik_pole_parent.constraints[0]
    f = 0.0

    for t in c.targets:
        if t.target == ik_pole_parent.id_data:
            if t.subtarget == ik_parent.name:
                f = t.weight

    # cancel ik_parent's damped track
    d_ik_pole = r_track.inverted() @ d_ik_pole * f + d_ik_pole * (1 - f)

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
    set_ik_pole(b['ik_pole'], b['ik_pole_parent'], b['parent'], b['ik_parent'], b['fk_1'], d_fk)


def snap_leg_ik2fk(b):
    d_fk = b['fk_2'].tail - b['parent'].head

    reset_pose(b['ik_foot_spin'])
    reset_pose(b['ik_heel'])
    set_ik_3(b['ik_3'], b['fk_3'], b['parent'], b['ik_target'], d_fk)
    set_ik_length(b['ik_length'], b['fk_length'], b['ik_target'], d_fk)
    set_ik_pole(b['ik_pole'], b['ik_pole_parent'], b['parent'], b['ik_parent'], b['fk_1'], d_fk)
    set_ik_4(b['ik_4'], b['ik_4_parent'], b['fk_4'], b['fk_4_parent'])
