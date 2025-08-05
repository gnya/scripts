import bpy

from re import match, split
from typing import Any


class ParseDataPathError(Exception):
    pass


def parse_path(path: str) -> tuple[str, str, int]:
    prop_path, index = path, -1

    if m := match(r'^(.+)\[(\d+)\]$', prop_path):
        prop_path = m.group(1)
        index = int(m.group(2))

    if not (m := match(r'^(.+|)(\[".+"\]|\.[^."]+)$', prop_path)):
        raise ParseDataPathError(f'"{path}": parsing data path was failed.')

    data_path = m.group(1)
    prop = m.group(2)
    prop = prop[1:] if prop.startswith('.') else prop

    return data_path, prop, index


def get_data(path: str, data: Any | None = None) -> Any:
    if not data and path.startswith('bpy'):
        data = bpy
        path = path[4:]

    for path_or_key in split(r'[\[\]]+', path):
        if not path_or_key:
            continue
        elif path_or_key.isdecimal():
            data = data[int(path_or_key)]
        elif path_or_key.startswith(('\'', '"')):
            data = data[path_or_key[1:-1]]
        else:
            for prop in path_or_key.split('.'):
                if not prop:
                    continue

                data = getattr(data, prop)

    return data


def get_value(prop: str, index: int, data: Any) -> Any:
    if prop.startswith('['):
        value = data[prop[2:-2]]
    else:
        value = getattr(data, prop)

    value = value[index] if index != -1 else value

    return value
