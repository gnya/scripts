import bpy

from bpy.types import UILayout
from re import match, split
from typing import Any

from .collect import _collect_contents


class ParseDataPathError(Exception):
    pass


class OperatorNotFoundError(Exception):
    pass


class PropertyNotFoundError(Exception):
    pass


def _exists_operator(path: str) -> bool:
    try:
        bpy.ops._op_as_string(path)
    except AttributeError:
        return False

    return True


def draw_operator(layout: UILayout, content: tuple, **kwargs):
    path, (text, icon, order, width), enum_arg, args = content
    icon = icon if icon else 'NONE'

    if not _exists_operator(path):
        raise OperatorNotFoundError(f'"{path}" wasn\'t found.')

    if enum_arg:
        op = layout.operator_menu_enum(path, enum_arg, text=text, icon=icon, translate=False)
    else:
        op = layout.operator(path, text=text, icon=icon, translate=False)

    for key, value in args.items():
        if hasattr(op, key):
            setattr(op, key, value)

    for key, value in kwargs.items():
        if hasattr(op, key):
            setattr(op, key, value)


def _parse_path(path: str) -> tuple[str, str, int]:
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


def _get_data(path: str, data: Any | None = None) -> Any:
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


def _get_value(prop: str, index: int, data: Any | None = None) -> Any:
    if prop.startswith('['):
        value = data[prop[2:-2]]
    else:
        value = getattr(data, prop)

    value = value[index] if index != -1 else value

    return value


def draw_property(layout: UILayout, content: tuple, data: Any | None = None):
    path, (text, icon, order, width) = content
    data_path, prop, index = _parse_path(path)

    try:
        data = _get_data(data_path, data)
        value = _get_value(prop, index, data)
    except (AttributeError, IndexError) as e:
        raise PropertyNotFoundError(f'"{path}" wasn\'t found.') from e

    text = text(value) if callable(text) else text
    icon = icon(value) if callable(icon) else icon
    icon = icon if icon else 'NONE'

    layout.prop(data, prop, index=index, text=text, icon=icon, translate=False, toggle=1)


def draw_group(layout: UILayout, contents: dict | tuple[dict], data: Any | None = None, **kwargs):
    content_list = _collect_contents(contents)
    content_list = sorted(content_list, key=lambda c: c[1][2])

    _layout = layout
    width_scale = 1.0

    for c in content_list:
        width = c[1][3]
        width_factor = width_scale * width

        if width_factor < 1.0:
            _layout = _layout.split(align=True, factor=width_factor)

        if len(c) == 4:
            draw_operator(_layout, c, **kwargs)
        else:
            draw_property(_layout, c, data)

        if width_factor >= 1.0:
            _layout = layout
            width_scale = 1.0
        else:
            width_scale = width_scale / (1.0 - width_factor)


def _marge_groups(contents: tuple[dict]):
    marged = {}

    for content_dict in contents:
        for group, c in content_dict.items():
            if group not in marged:
                marged[group] = (c,)
            else:
                marged[group].add(c)

    return marged


def draw(layout: UILayout, contents: dict | tuple[dict], data: Any | None = None, **kwargs):
    if isinstance(contents, tuple):
        contents = _marge_groups(contents)

    is_first = True

    for group, c in contents.items():
        if is_first:
            is_first = False
        else:
            layout.separator()

        col = layout.column(align=True)

        if group:
            col.label(text=group, translate=False)

        draw_group(col, c, data, **kwargs)
