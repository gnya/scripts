def has_driver(constraint, property):
    data = constraint.id_data.animation_data
    path = constraint.path_from_id(property)

    for d in data.drivers:
        if d.data_path == path:
            return True

    return False
