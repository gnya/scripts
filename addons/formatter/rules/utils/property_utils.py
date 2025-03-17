def reset_properties(data, properties, defaults):
    info = []

    for p in properties:
        prop = data.rna_type.properties[p]
        value = getattr(data, p)
        default = defaults[p] if p in defaults else prop.default

        if value != default:
            info.append(f'{p}({value} != {default})')
            setattr(data, p, default)

    if info:
        return False, ', '.join(info)

    return True, ''
