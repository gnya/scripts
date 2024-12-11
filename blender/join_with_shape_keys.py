# blender 3.6.0
import bpy


# Apply current shape key to object.
def apply_all_shape_keys(obj):
    c = bpy.context.copy()
    c['object'] = obj
    with bpy.context.temp_override(**c):
        bpy.ops.object.shape_key_remove(all=True, apply_mix=True)


# Join multiple objects into one object.
def join_objects(objs):
    meshes = set()

    for o in objs[1:]:
        meshes.add(o.data)

    c = bpy.context.copy()
    c['active_object'] = objs[0]
    c['selected_editable_objects'] = objs
    # Using temp_override crashes, so use the old way.
    bpy.ops.object.join(c)

    # The mesh data is still there, so I'll delete it.
    for m in meshes:
        bpy.data.meshes.remove(m)

    return c['active_object']


# Apply only a single shape key to an object.
def apply_single_shape_key(obj, key):
    shape_keys = obj.data.shape_keys

    if shape_keys is None:
        return

    keys = shape_keys.key_blocks

    for k in keys:
        k.value = 0.0

    if key in keys:
        keys[key].value = 1.0

    apply_all_shape_keys(obj)


# Join multiple objects into one object with a shape key of the same name.
def join_with_shape_key(objs, key):
    applied_objs = []

    for o in objs:
        # Create a duplicate of an object.
        new_o = o.copy()
        new_o.data = o.data.copy()

        apply_single_shape_key(new_o, key)
        applied_objs.append(new_o)

        # Link to scene collection to be able to join.
        bpy.context.scene.collection.objects.link(new_o)

    return join_objects(applied_objs)


# Adding a shape key to an object.
def shape_key_add(obj):
    c = bpy.context.copy()
    c['object'] = obj
    with bpy.context.temp_override(**c):
        bpy.ops.object.shape_key_add(from_mix=False)


# Join another object to an object as a shape key.
def join_shapes(source, target, key):
    c = bpy.context.copy()
    c['active_object'] = target
    c['selected_editable_objects'] = [target, source]
    with bpy.context.temp_override(**c):
        bpy.ops.object.join_shapes()
    target.data.shape_keys.key_blocks[-1].name = key


# Completely delete multiple objects.
def delete_objects(objs):
    meshes = set()

    for o in objs:
        meshes.add(o.data)
        bpy.data.objects.remove(o)

    for m in meshes:
        bpy.data.meshes.remove(m)


# Join multiple shape keyed objects into a single object.
def join_with_shape_keys(objs):
    # Enumerates the names of shape keys that the selected mesh has.
    keys = set()

    for o in objs:
        shape_keys = o.data.shape_keys

        if shape_keys is not None:
            for s in shape_keys.key_blocks[1:]:
                keys.add(s.name)

    # Mesh join for each shape key.
    obj = join_with_shape_key(mesh_objects, '')
    shapes = {}

    for k in keys:
        shapes[k] = join_with_shape_key(objs, k)

    # Sort by key order.
    shapes = dict(sorted(shapes.items()))

    # Join each shape key to the base object.
    shape_key_add(obj)

    for k, o in shapes.items():
        join_shapes(o, obj, k)

    obj.name = ' '.join([o.name for o in objs])

    # Delete unused objects.
    delete_objects(list(shapes.values()))


if __name__ == '__main__':
    # Extract only the mesh from the selected objects.
    mesh_objects = []

    for o in bpy.context.selected_objects:
        if o.type == 'MESH':
            mesh_objects.append(o)

    # Join shape keyed objects.
    join_with_shape_keys(mesh_objects)
