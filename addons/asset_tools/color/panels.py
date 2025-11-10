import bpy

from asset_tools import utils


UI_CONTENTS = {
    'Light': {
        '$view3d.color_attach_light': ('Attach', 'LIGHT', 0, 1.0)
    }
}


def _collect_props(props, group, path, name, links):
    for link in links:
        n = link.from_socket.node

        if n.type == 'TEX_IMAGE':
            key = (group, f'{path}.nodes["{n.name}"]', 'image')

            if key in props:
                props[key].append(name)
            else:
                props[key] = [name]

        for i in n.inputs:
            if i.is_linked:
                _collect_props(props, group, path, name, i.links)


def _ui_contents(obj):
    node_trees = set()
    code = obj.name.split('_')[0]

    for n in bpy.data.node_groups:
        s = n.name.split('_')

        if s[-1] == 'COLOR' and s[0] == code:
            node_trees.add(n)

    props = {}

    for nt in node_trees:
        path = repr(nt)

        if n := nt.nodes['Group Output']:
            for i in range(len(n.inputs)):
                n_in = n.inputs[i]

                if n_in.type != 'RGBA':
                    continue

                if n_in.is_linked:
                    _collect_props(props, nt.name, path, n_in.name, n_in.links)
                else:
                    p = f'{path}.nodes["Group Output"].inputs[{i}]'
                    props[(nt.name, p, 'default_value')] = [n_in.name]

    ui_contents = {}

    for key, names in props.items():
        group, path, prop = key

        if group not in ui_contents:
            ui_contents[group] = {}

        ui_contents[group][f'{path}.{prop}'] = (', '.join(names), '', 0, 0.5)

    return ui_contents


class VIEW3D_PT_color(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_color'
    bl_label = 'Color'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Color'

    @classmethod
    def poll(cls, context):
        return utils.is_rig(context.active_object)

    def draw(self, context):
        obj = context.active_object
        col = self.layout.column(align=True)

        utils.ui.draw(col, UI_CONTENTS, obj)
        utils.ui.draw(col, _ui_contents(obj))
