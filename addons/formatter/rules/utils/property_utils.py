def reset_property(data, property, default=None):
    nesting = property.split('.', 1)

    if len(nesting) > 1:
        d = getattr(data, nesting[0])

        return reset_property(d, nesting[1], default)

    p = data.rna_type.properties[property]
    is_array = getattr(p, 'is_array', False)

    value = getattr(data, property)
    value = list(value) if is_array else value

    if default is None:
        default = list(p.default_array) if is_array else p.default

    if value != default:
        setattr(data, property, default)

        return False

    return True


def reset_properties(data, properties):
    resetted = []

    for p, default in properties.items():
        if not reset_property(data, p, default=default):
            resetted.append(p)

    return resetted
