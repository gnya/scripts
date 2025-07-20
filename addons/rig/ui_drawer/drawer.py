import bpy  # noqa: F401
import re


def _collect_ops(contents, path, props):
    for prop in props.keys():
        group, text, icon, order, width = props[prop]

        if group not in contents:
            contents[group] = []

        contents[group].append((order, path, prop, None, text, icon, -1, width))


def _collect_props(contents, data, props):
    for prop in props.keys():
        m = re.split(r'[\"\[\]]+', prop)
        p = m[0] if m[0] else prop
        i = int(m[1]) if m[0] and len(m) > 1 else -1
        custom_p = m[1] if not m[0] and len(m) > 1 else ''

        value = None

        if hasattr(data, p):
            value = getattr(data, p)
        elif custom_p in data.keys():
            value = data[custom_p]

        value = value[i] if i >= 0 else value

        if value is not None:
            group, text, icon, order, width = props[prop]

            if group not in contents:
                contents[group] = []

            contents[group].append((order, data, p, value, text, icon, i, width))


def collect_contents(contents, data, props):
    for path, p in props.items():
        if path.startswith('$'):
            _collect_ops(contents, path[1:], p)
        else:
            data_path = repr(data)

            if not path or path.startswith('['):
                data_path += path
            else:
                data_path += '.' + path

            try:
                d = eval(f'{data_path}')
            except (AttributeError, IndexError):
                continue
            else:
                _collect_props(contents, d, p)


def draw_contents(layout, contents, operator_args={}):
    groups = sorted(contents.keys(), key=lambda g: contents[g][0][0])
    is_first = True

    for group in groups:
        if is_first:
            is_first = False
        else:
            layout.separator()

        col = layout.column(align=True)
        split = None
        total_width = 0.0
        width_scale = 1.0

        if group:
            col.label(text=group, translate=False)

        c = sorted(contents[group], key=lambda c: c[0])

        for _, d, p, v, t, icon, i, width in c:
            t = t(v) if callable(t) else t
            icon = icon(v) if callable(icon) else icon

            icon = icon if icon else 'NONE'
            width = min(width, 1.0 - total_width)
            factor = width_scale * width
            ui = split if split else col

            if factor < 1.0:
                split = ui.split(align=True, factor=factor)
                ui = split

            if isinstance(d, str):
                op = None

                if p:
                    op = ui.operator_menu_enum(d, p, text=t, icon=icon, translate=False)
                else:
                    op = ui.operator(d, text=t, icon=icon, translate=False)

                for name, arg in operator_args.items():
                    if hasattr(op, name):
                        setattr(op, name, arg)
            else:
                ui.prop(d, p, text=t, icon=icon, translate=False, toggle=1, index=i)

            total_width += width

            if factor >= 1.0:
                total_width = 0.0
                width_scale = 1.0
                split = None if split else split
            else:
                width_scale = width_scale / (1.0 - factor)
