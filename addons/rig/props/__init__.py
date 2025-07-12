import bpy
import re


class VIEW3D_PT_rig_props(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_show'
    bl_label = 'Properties'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'VIEW3D_PT_rig_main'
    bl_order = 1

    @staticmethod
    def _collect_props(props, data, info):
        for p in info.keys():
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
                group, text, order = info[p]

                if group not in props:
                    props[group] = []

                props[group].append((data, prop, text, index, order))

    @staticmethod
    def _draw_props(layout, props):
        groups = sorted(props.keys(), key=lambda g: props[g][0][4])

        for group in groups:
            layout.separator()
            col = layout.column(align=True)
            p = sorted(props[group], key=lambda p: p[4])

            for data, prop, text, index, _ in p:
                col.prop(data, prop, text=text, translate=False, toggle=1, index=index)

    def draw(self, context):
        armature = context.active_object
        bones = armature.pose.bones

        prop_info = {
            '': {
                '["quality"]': ('Quality', 'Quality', 0),
                '["preview_quality"]': ('Quality', 'Preview Quality', 1),
                '["show_gloves"]': ('Show/Hide Clothes', 'Gloves', 100),
                'layers[0]': ('Show/Hide Body', 'Fingers', 201),
                'layers[1]': ('Show/Hide Body', 'Arm IK', 202),
                'layers[2]': ('Show/Hide Body', 'Arm FK', 203),
                'layers[16]': ('Show/Hide Body', 'Root & Spine', 204),
                'layers[17]': ('Show/Hide Body', 'Leg IK', 205),
                'layers[18]': ('Show/Hide Body', 'Lef FK', 206),
                'layers[4]': ('Show/Hide Bones', 'Eyebrows', 300),
                'layers[5]': ('Show/Hide Bones', 'Eye Target', 301),
                'layers[6]': ('Show/Hide Bones', 'Expressions', 302),
                'layers[7]': ('Show/Hide Bones', 'Lattice', 303),
                'layers[20]': ('Show/Hide Bones', 'Eyes', 304),
                'layers[21]': ('Show/Hide Bones', 'Mouth', 305),
                'layers[22]': ('Show/Hide Bones', 'Tooth & Tongue', 306),
                'layers[23]': ('Show/Hide Props', 'Properties', 600),
            },
            'CTR_properties_body': {
                '["auto_ctrl_switching"]': ('Show/Hide Body', 'Auto Switch (Body)', 200)
            },
            'CTR_properties_expression': {
                '["auto_ctrl_switching"]': ('Show/Hide Face', 'Auto Switch (Expression)', 400),
                '["show_double_eyelid"]': ('Show/Hide Face', 'Double Eyelid', 401),
                '["show_eyelashes_A"]': ('Show/Hide Face', 'Eyelashes A', 402),
                '["show_lip_line"]': ('Show/Hide Face', 'Lip Line', 403),
                '["show_eyelashes_B"]': ('Show/Hide Face', 'Eyelashes B', 404),
                '["show_sweat.L"]': ('Show/Hide Face', 'Sweat L', 405),
                '["show_sweat.R"]': ('Show/Hide Face', 'Sweat R', 406),
                '["show_wrinkles_A"]': ('Show/Hide Face', 'Wrinkles A', 407),
                '["show_wrinkles_B"]': ('Show/Hide Face', 'Wrinkles B', 408)
            },
            'CTR_properties_head': {
                '["head_hinge"]': ('Head', 'Head Hinge', 500),
                '["neck_hinge"]': ('Head', 'Neck Hinge', 501),
                '["sticky_eyesockets"]': ('Head', 'Sticky Eyesockets', 502),
                '["reduce_perspective"]': ('Head', 'Reduce Perspective', 503)
            },
            'CTR_lattice_target': {
                'target': ('Head', 'Camera', 504)
            }
        }

        props = {}

        VIEW3D_PT_rig_props._collect_props(props, armature, prop_info[''])
        VIEW3D_PT_rig_props._collect_props(props, armature.data, prop_info[''])

        for b in bones:
            if b.name in prop_info:
                VIEW3D_PT_rig_props._collect_props(props, b, prop_info[b.name])

        if 'CTR_lattice_target' in bones and bones['CTR_lattice_target'].constraints:
            con = bones['CTR_lattice_target'].constraints[0]
            VIEW3D_PT_rig_props._collect_props(props, con, prop_info['CTR_lattice_target'])

        VIEW3D_PT_rig_props._draw_props(self.layout, props)
