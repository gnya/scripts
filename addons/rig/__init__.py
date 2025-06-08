import bpy
from . import ik_fk


bl_info = {
    'name': 'Rig',
    'author': 'gnya',
    'version': (0, 1, 1),
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


class VIEW3D_PT_rig_main(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_main'
    bl_label = 'Rig'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_order = 1

    @classmethod
    def poll(self, context):
        check, _, _, _ = ik_fk.check_ik_fk_bone(context.active_pose_bone)

        return check

    def draw(self, context):
        check, group, _, lr = ik_fk.check_ik_fk_bone(context.active_pose_bone)

        if check:
            layout = self.layout
            c = layout.column(align=True)

            c.label(text=f'Snap FK/IK ({group}.{lr})')

            op_ik_fk = c.operator('view3d.rig_snap_ik_to_fk', icon='SNAP_ON')
            op_ik_fk.bone_group = group
            op_ik_fk.bone_lr = lr

            op_fk_ik = c.operator('view3d.rig_snap_fk_to_ik', icon='SNAP_ON')
            op_fk_ik.bone_group = group
            op_fk_ik.bone_lr = lr


def register():
    bpy.utils.register_class(VIEW3D_OT_rig_snap_ik_to_fk)
    bpy.utils.register_class(VIEW3D_OT_rig_snap_fk_to_ik)
    bpy.utils.register_class(VIEW3D_PT_rig_main)


def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_rig_snap_ik_to_fk)
    bpy.utils.unregister_class(VIEW3D_OT_rig_snap_fk_to_ik)
    bpy.utils.unregister_class(VIEW3D_PT_rig_main)


if __name__ == '__main__':
    register()
