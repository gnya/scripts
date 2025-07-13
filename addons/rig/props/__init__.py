import bpy
import copy
import re
from . import info


class VIEW3D_PT_rig_props(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_show'
    bl_label = 'Properties'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'VIEW3D_PT_rig_main'
    bl_order = 1

    @staticmethod
    def _collect_props(props, data, prop_info):
        for p in prop_info.keys():
            prop = p
            index = -1
            custom_prop = ''

            m = re.split(r'[\"\[\]]+', p)

            if m[0]:
                prop = m[0]

                if len(m) > 1:
                    index = int(m[1])
            elif len(m) > 1:
                custom_prop = p.strip('"[]')

            if hasattr(data, prop) or custom_prop in data.keys():
                group, text, order, width = prop_info[p]

                if group not in props:
                    props[group] = []

                props[group].append((data, prop, text, index, order, width))

    @staticmethod
    def _draw_props(layout, props):
        groups = sorted(props.keys(), key=lambda g: props[g][0][4])

        for group in groups:
            layout.separator()
            col = layout.column(align=True)
            split = None
            total_width = 0.0
            width_scale = 1.0

            p = sorted(props[group], key=lambda p: p[4])

            for i in range(len(p)):
                data, prop, text, index, _, width = p[i]
                width = min(width, 1.0 - total_width)
                factor = width_scale * width
                ui = split if split else col

                if factor < 1.0:
                    split = ui.split(align=True, factor=factor)
                    ui = split

                ui.prop(data, prop, text=text, translate=False, toggle=1, index=index)

                total_width += width

                if factor >= 1.0:
                    total_width = 0.0
                    width_scale = 1.0
                    split = None if split else split
                else:
                    width_scale = width_scale / (1.0 - factor)

    def draw(self, context):
        obj = context.active_object
        bones = obj.pose.bones if obj.pose else {}
        asset_name = obj.name.split('_')[0]
        p_info = info.RIG_PROP_INFO['']
        p_info = copy.deepcopy(p_info)
        p_asset_info = info.RIG_PROP_INFO.get(asset_name, {})
        p_asset_info = copy.deepcopy(p_asset_info)

        for k, v in p_asset_info.items():
            if k not in p_info:
                p_info[k] = {}

            p_info[k].update(v)

        props = {}

        VIEW3D_PT_rig_props._collect_props(props, obj, p_info[''])

        if obj.data:
            VIEW3D_PT_rig_props._collect_props(props, obj.data, p_info[''])

        for b in bones:
            if b.name in p_info:
                VIEW3D_PT_rig_props._collect_props(props, b, p_info[b.name])

        if 'CTR_lattice_target' in bones and bones['CTR_lattice_target'].constraints:
            c = bones['CTR_lattice_target'].constraints[0]
            VIEW3D_PT_rig_props._collect_props(props, c, p_info['CTR_lattice_target'])

        col = self.layout.column(align=True)
        VIEW3D_PT_rig_props._draw_props(col, props)
