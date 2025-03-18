from bpy_types import bpy_types


def compare_array(p0, p1):
    for v0, v1 in zip(p0, p1):
        if v0 != v1:
            return False

    return True


def reset_properties(data, properties, defaults):
    info = []

    for p in properties:
        value = getattr(data, p)
        prop = data.rna_type.properties[p]
        default = defaults.get(p, prop.default)

        if not prop.is_array:
            default = defaults.get(p, prop.default)

            if value != default:
                info.append(f'{p}({value} != {default})')
                setattr(data, p, default)
        else:
            default = defaults.get(p, prop.default_array)

            if not compare_array(value, default):
                info.append(f'{p}')
                setattr(data, p, default)

    if info:
        return False, ', '.join(info)

    return True, ''
