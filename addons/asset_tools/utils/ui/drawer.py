import bpy

from bpy.types import UILayout
from re import match
from typing import Any

from .collect import _collect_contents


class ParseDataPathError(Exception):
    pass


class OperatorNotFoundError(Exception):
    pass


class PropertyNotFoundError(Exception):
    pass


def _exists_operator(path: str) -> bool:
    op = bpy.ops

    for p in path.split('.'):
        if p in dir(op):
            op = getattr(op, p)
        else:
            return False

    return True


def _parse_path(path: str, data: Any | None = None) -> tuple[str, str, str, int]:
    head_path = repr(data) if data else ''

    if not head_path:
        full_path = path
    elif not path:
        full_path = head_path
    elif path.startswith('['):
        full_path = head_path + path
    else:
        full_path = head_path + '.' + path

    prop_path, index = full_path, -1

    if m := match(r'^(.+)\[(\d+)\]$', prop_path):
        prop_path, index = m.group(1), int(m.group(2))

    if not (m := match(r'^(.+)(\[".+"\]|\.[^."]+)$', prop_path)):
        raise ParseDataPathError(f'"{full_path}": parsing data path was failed.')

    data_path, prop = m.group(1), m.group(2)
    prop = prop[1:] if prop.startswith('.') else prop

    return full_path, data_path, prop, index


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


def draw_property(layout: UILayout, content: tuple, data: Any | None = None):
    path, (text, icon, order, width) = content
    full_path, data_path, prop, index = _parse_path(path, data)

    try:
        v = eval(full_path)
        d = eval(data_path)
    except (AttributeError, IndexError) as e:
        raise PropertyNotFoundError(f'"{full_path}" wasn\'t found.') from e

    text = text(v) if callable(text) else text
    icon = icon(v) if callable(icon) else icon
    icon = icon if icon else 'NONE'

    layout.prop(d, prop, index=index, text=text, icon=icon, translate=False, toggle=1)


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
