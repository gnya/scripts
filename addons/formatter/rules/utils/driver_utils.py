def has_driver(armature, bone, constraint, prop_name):
    path = f'pose.bones["{bone.name}"].constraints["{constraint.name}"].{prop_name}'

    for d in armature.animation_data.drivers:
        if d.data_path == path:
            return True

    return False
