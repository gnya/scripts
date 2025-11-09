from re import sub


def make_unique_name(name: str, names: list[str]) -> str:
    base = sub(r'.\d{3}$', '', name)
    i = 1

    while name in names:
        name = f'{base}.{i:03d}'
        i += 1

    return name
