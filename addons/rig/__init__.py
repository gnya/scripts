import bpy
from . import ik_fk

bl_info = {
    'name': 'Rig',
    'author': 'gnya',
    'version': (0, 1, 2),
    'blender': (3, 6, 0),
    'description':
        'A set of tools to make character rigs easier to use. '
        '(For my personal project.)',
    'category': 'Utility'
}


class VIEW3D_OT_rig_snap_ik_to_fk(bpy.types.Operator):
    bl_idname = 'view3d.rig_snap_ik_to_fk'
    bl_label = 'IK → FK'
    bl_description = 'Snap IK to FK'
    bl_options = {'UNDO'}

    bone_group: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722
    bone_lr: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722

    def execute(self, context):
        bones, missing = ik_fk.ik_fk_bones(context.pose_object, self.bone_group, self.bone_lr)

        if not bones:
            self.report({'ERROR'}, 'Required ik/fk bones not found.')

            return {'CANCELLED'}
        elif missing:
            self.report({'ERROR'}, f'Required ik/fk bones are missing. : {missing}')

            return {'CANCELLED'}

        if self.bone_group == 'arm':
            ik_fk.snap_arm_ik2fk(bones)
        elif self.bone_group == 'leg':
            ik_fk.snap_leg_ik2fk(bones)

        return {'FINISHED'}


class VIEW3D_OT_rig_snap_fk_to_ik(bpy.types.Operator):
    bl_idname = 'view3d.rig_snap_fk_to_ik'
    bl_label = 'FK → IK'
    bl_description = 'Snap FK to IK'
    bl_options = {'UNDO'}

    bone_group: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722
    bone_lr: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722

    def execute(self, context):
        bones, missing = ik_fk.ik_fk_bones(context.pose_object, self.bone_group, self.bone_lr)

        if not bones:
            self.report({'ERROR'}, 'Required ik/fk bones not found.')

            return {'CANCELLED'}
        elif missing:
            self.report({'ERROR'}, f'Required ik/fk bones are missing. : {missing}')

            return {'CANCELLED'}

        if self.bone_group == 'arm':
            ik_fk.snap_arm_fk2ik(bones)
        elif self.bone_group == 'leg':
            ik_fk.snap_leg_fk2ik(bones)

        return {'FINISHED'}


# TODO Replace ikfk bone props to this.
class RigProperties(bpy.types.PropertyGroup):
    ui_ikfk: bpy.props.BoolProperty(default=True)  # type: ignore # noqa: F722


class VIEW3D_PT_rig_main(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_main'
    bl_label = 'Rig'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_order = 1

    @classmethod
    def poll(self, context):
        obj = context.active_object

        if obj and obj.type == 'ARMATURE':
            return True

        return False

    @staticmethod
    def draw(self, context):
        pass


class VIEW3D_PT_rig_show(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_show'
    bl_label = 'Show/Hide'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'VIEW3D_PT_rig_main'
    bl_order = 1

    @staticmethod
    def draw(self, context):
        layout = self.layout

        armature = context.active_object
        props_body = armature.pose.bones["CTR_properties_body"]
        props_expr = armature.pose.bones["CTR_properties_expression"]
        props_head = armature.pose.bones["CTR_properties_head"]

        col = layout.column(align=True)
        col.prop(props_body, '["auto_ctrl_switching"]', toggle=1, text='Auto Switch (Body)')

        col.separator()

        col = layout.column(align=True)
        col.prop(props_expr, '["auto_ctrl_switching"]', toggle=1, text='Auto Switch (Expression)')
        col.prop(props_expr, '["show_double_eyelid"]', toggle=1, text='Double Eyelid')
        col.prop(props_expr, '["show_eyelashes_A"]', toggle=1, text='Eyelashes A')
        col.prop(props_expr, '["show_lip_line"]', toggle=1, text='Lip Line')

        col = layout.column(align=True)
        col.prop(props_expr, '["show_eyelashes_B"]', toggle=1, text='Eyelashes B')
        col.prop(props_expr, '["show_sweat.L"]', toggle=1, text='Sweat L')
        col.prop(props_expr, '["show_sweat.R"]', toggle=1, text='Sweat R')
        col.prop(props_expr, '["show_wrinkles_A"]', toggle=1, text='Wrinkles A')
        col.prop(props_expr, '["show_wrinkles_B"]', toggle=1, text='Wrinkles B')

        col.separator()

        col = layout.column(align=True)
        col.prop(props_head, '["head_hinge"]', text='Head Hinge')
        col.prop(props_head, '["neck_hinge"]', text='Neck Hinge')
        col.prop(props_head, '["sticky_eyesockets"]', text='Sticky Eyesockets')

        target = armature.pose.bones["CTR_lattice_target"]

        if target.constraints:
            con = target.constraints[0]

            layout.prop(props_head, '["reduce_perspective"]', text='Reduce Perspective')
            layout.prop(con, 'target', toggle=1, text='Camera')


class VIEW3D_PT_rig_ikfk(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_ikfk'
    bl_label = 'IK/FK'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = 'VIEW3D_PT_rig_main'
    bl_order = 1

    @classmethod
    def poll(self, context):
        bones = context.selected_pose_bones

        if not bones:
            return False

        groups = ik_fk.check_ik_fk_bones(bones)

        return True if groups else False

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        is_first = True

        bones = context.selected_pose_bones
        armature = context.active_object
        groups = ik_fk.check_ik_fk_bones(bones)
        props = armature.pose.bones["CTR_properties_body"]

        for group, _, lr in groups:
            if is_first:
                is_first = False
            else:
                col.separator()

            col.box().label(text=f'{armature.name} ({group}.{lr})')

            op_ik_fk = col.operator('view3d.rig_snap_ik_to_fk', icon='SNAP_ON')
            op_ik_fk.bone_group = group
            op_ik_fk.bone_lr = lr

            op_fk_ik = col.operator('view3d.rig_snap_fk_to_ik', icon='SNAP_ON')
            op_fk_ik.bone_group = group
            op_fk_ik.bone_lr = lr

            col.prop(props, f'["fk_{group}.{lr}"]', text='IK-FK')
            col.prop(props, f'["ik_stretch_{group}s"]', text='IK Stretch')
            col.prop(props, f'["ik_pole_follow_{group}.{lr}"]', text='IK Pole Follow')


def register():
    bpy.utils.register_class(RigProperties)

    bpy.types.WindowManager.rig_addon_properties = \
        bpy.props.PointerProperty(type=RigProperties)

    bpy.utils.register_class(VIEW3D_OT_rig_snap_ik_to_fk)
    bpy.utils.register_class(VIEW3D_OT_rig_snap_fk_to_ik)
    bpy.utils.register_class(VIEW3D_PT_rig_main)
    bpy.utils.register_class(VIEW3D_PT_rig_show)
    bpy.utils.register_class(VIEW3D_PT_rig_ikfk)


def unregister():
    bpy.utils.unregister_class(RigProperties)

    del bpy.types.WindowManager.rig_addon_properties

    bpy.utils.unregister_class(VIEW3D_OT_rig_snap_ik_to_fk)
    bpy.utils.unregister_class(VIEW3D_OT_rig_snap_fk_to_ik)
    bpy.utils.unregister_class(VIEW3D_PT_rig_main)
    bpy.utils.unregister_class(VIEW3D_PT_rig_show)
    bpy.utils.unregister_class(VIEW3D_PT_rig_ikfk)


if __name__ == '__main__':
    register()
