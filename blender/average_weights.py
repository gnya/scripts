import bpy
import bmesh
import re


def selected_verts(obj):
    active_vert_id = -1
    vert_ids = []

    mesh = bmesh.from_edit_mesh(obj.data)
    hist = list(reversed(mesh.select_history))

    if len(hist) and isinstance(hist[0], bmesh.types.BMVert):
        active_vert_id = hist[0].index

    for v in mesh.verts:
        if v.select:
            vert_ids.append(v.index)

    return (active_vert_id, vert_ids)


def deform_groups(obj):
    groups = []

    for g in obj.vertex_groups:
        if re.match('DEF_.*', g.name):
            groups.append(g.index)

    return groups


def get_average_weights(obj, vert_ids):
    sum = {}

    groups = deform_groups(obj)
    mesh = bmesh.from_edit_mesh(obj.data)
    deform = mesh.verts.layers.deform.active

    for v in vert_ids:
        for g, w in mesh.verts[v][deform].items():
            if g in groups:
                if g in sum:
                    sum[g] += w
                else:
                    sum[g] = w

    for g in sum.keys():
        sum[g] /= len(vert_ids)

    return sum


def set_weights(obj, vert_id, weights):
    mesh = bmesh.from_edit_mesh(obj.data)
    deform = mesh.verts.layers.deform.active

    for g, w in weights.items():
        mesh.verts[vert_id][deform][g] = w

    bmesh.update_edit_mesh(obj.data)


if __name__ == '__main__':
    obj = bpy.context.active_object
    active_vert_id, vert_ids = selected_verts(obj)

    if active_vert_id != -1 and len(vert_ids) > 2:
        vert_ids.remove(active_vert_id)
        weights = get_average_weights(obj, vert_ids)
        set_weights(obj, active_vert_id, weights)
