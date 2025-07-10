import bpy


class VIEW3D_PT_rig_props(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_show'
    bl_label = 'Show/Hide'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'VIEW3D_PT_rig_main'
    bl_order = 1

    def draw(self, context):
        layout = self.layout

        armature = context.active_object
        bones = armature.pose.bones

        col = layout.column(align=True)

        if 'preview_quality' in armature:
            col.prop(armature, '["preview_quality"]', toggle=1, text='Preview Quality')

        if 'quality' in armature:
            col.prop(armature, '["quality"]', toggle=1, text='Quality')

        if 'show_gloves' in armature:
            col.prop(armature, '["show_gloves"]', toggle=1, text='Gloves')

        if 'CTR_properties_body' in bones:
            col.separator()

            col = layout.column(align=True)
            props_body = bones['CTR_properties_body']

            col.prop(props_body, '["auto_ctrl_switching"]', toggle=1, text='Auto Switch (Body)')

        if 'CTR_properties_expression' in bones:
            col.separator()

            col = layout.column(align=True)
            props_expr = bones['CTR_properties_expression']

            col.prop(props_expr, '["auto_ctrl_switching"]', toggle=1, text='Auto Switch (Expr)')
            col.prop(props_expr, '["show_double_eyelid"]', toggle=1, text='Double Eyelid')
            col.prop(props_expr, '["show_eyelashes_A"]', toggle=1, text='Eyelashes A')
            col.prop(props_expr, '["show_lip_line"]', toggle=1, text='Lip Line')

            col = layout.column(align=True)

            col.prop(props_expr, '["show_eyelashes_B"]', toggle=1, text='Eyelashes B')
            col.prop(props_expr, '["show_sweat.L"]', toggle=1, text='Sweat L')
            col.prop(props_expr, '["show_sweat.R"]', toggle=1, text='Sweat R')
            col.prop(props_expr, '["show_wrinkles_A"]', toggle=1, text='Wrinkles A')
            col.prop(props_expr, '["show_wrinkles_B"]', toggle=1, text='Wrinkles B')

        if 'CTR_properties_head' in bones:
            col.separator()

            col = layout.column(align=True)
            props_head = bones['CTR_properties_head']

            col.prop(props_head, '["head_hinge"]', text='Head Hinge')
            col.prop(props_head, '["neck_hinge"]', text='Neck Hinge')
            col.prop(props_head, '["sticky_eyesockets"]', text='Sticky Eyesockets')

            if 'CTR_lattice_target' in bones and bones['CTR_lattice_target'].constraints:
                con = bones['CTR_lattice_target'].constraints[0]

                layout.prop(props_head, '["reduce_perspective"]', text='Reduce Perspective')
                layout.prop(con, 'target', text='Camera')
