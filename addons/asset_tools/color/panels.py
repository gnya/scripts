import bpy
import re

from asset_tools import utils


UI_CONTENTS = {
    '$view3d.rig_attach_light': {
        '': ('Light', 'Attach', 'LIGHT', 0, 1.0)
    }
}


def _collect_props(props, group, name, links):
    for link in links:
        n = link.from_socket.node

        if n.type == 'TEX_IMAGE':
            key = (group, repr(n), 'image')

            if key in props:
                props[key].append(name)
            else:
                props[key] = [name]

        for i in n.inputs:
            if i.links:
                _collect_props(props, group, name, i.links)


def _ui_contents(obj):
    materials = set()

    for o in obj.children_recursive:
        if o.type == 'MESH':
            for m in o.data.materials:
                materials.add(m)

    node_trees = set()

    for m in materials:
        for n in m.node_tree.nodes:
            if n.type == 'GROUP':
                if re.match(r'[^_]+_COLOR', n.node_tree.name):
                    node_trees.add(n.node_tree)

    props = {}

    for nt in node_trees:
        for n in nt.nodes:
            if n.type == 'GROUP_OUTPUT':
                for i in n.inputs:
                    if i.type == 'RGBA':
                        if i.links:
                            _collect_props(props, nt.name, i.name, i.links)
                        else:
                            props[(nt.name, repr(i), 'default_value')] = [i.name]

    ui_contents = {}

    for key, names in props.items():
        group, path, prop = key

        ui_contents[path] = {
            prop: (group, ', '.join(names), '', 0, 0.5)
        }

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

        contents = {}
        utils.ui.collect_contents(contents, obj, UI_CONTENTS)
        utils.ui.collect_contents(contents, None, _ui_contents(obj))

        col = self.layout.column(align=True)
        utils.ui.draw_contents(col, contents)
