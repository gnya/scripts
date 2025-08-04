import bpy

from .bones import ik_fk_bones

from .snap import snap_arm_ik2fk
from .snap import snap_arm_fk2ik
from .snap import snap_leg_ik2fk
from .snap import snap_leg_fk2ik


class VIEW3D_OT_rig_snap_ik_to_fk(bpy.types.Operator):
    bl_idname = 'view3d.rig_snap_ik_to_fk'
    bl_label = 'IK → FK'
    bl_description = 'Snap IK to FK'
    bl_options = {'UNDO'}

    bone_group: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722
    bone_lr: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722

    def execute(self, context):
        bones, missing = ik_fk_bones(context.snap_target, self.bone_group, self.bone_lr)

        if not bones:
            self.report({'ERROR'}, 'Required ik/fk bones not found.')

            return {'CANCELLED'}
        elif missing:
            self.report({'ERROR'}, f'Required ik/fk bones are missing. : {missing}')

            return {'CANCELLED'}

        if self.bone_group == 'arm':
            snap_arm_ik2fk(bones)
        elif self.bone_group == 'leg':
            snap_leg_ik2fk(bones)

        return {'FINISHED'}


class VIEW3D_OT_rig_snap_fk_to_ik(bpy.types.Operator):
    bl_idname = 'view3d.rig_snap_fk_to_ik'
    bl_label = 'FK → IK'
    bl_description = 'Snap FK to IK'
    bl_options = {'UNDO'}

    bone_group: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722
    bone_lr: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722

    def execute(self, context):
        bones, missing = ik_fk_bones(context.snap_target, self.bone_group, self.bone_lr)

        if not bones:
            self.report({'ERROR'}, 'Required ik/fk bones not found.')

            return {'CANCELLED'}
        elif missing:
            self.report({'ERROR'}, f'Required ik/fk bones are missing. : {missing}')

            return {'CANCELLED'}

        if self.bone_group == 'arm':
            snap_arm_fk2ik(bones)
        elif self.bone_group == 'leg':
            snap_leg_fk2ik(bones)

        return {'FINISHED'}


class VIEW3D_OT_rig_set_ik_parent(bpy.types.Operator):
    bl_idname = 'view3d.rig_set_ik_parent'
    bl_label = 'IK Parent'
    bl_description = 'Set IK Controller\'s parent'
    bl_options = {'UNDO'}

    bone_group: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722
    bone_lr: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722

    type: bpy.props.EnumProperty(
        items=[
            ('0', 'Root', ''),  # noqa: F722 F821
            ('1', 'Torso', ''),  # noqa: F722 F821
            ('2', 'Chest', '')  # noqa: F722 F821
        ],
        translation_context='Operator'  # noqa: F821
    )  # type: ignore

    def execute(self, context):
        if not context.props_body:
            self.report({'ERROR'}, 'Required bone is missing.')

            return {'CANCELLED'}

        prop = f'ik_{self.bone_group}_parent.{self.bone_lr}'

        if prop not in context.props_body:
            self.report({'ERROR'}, f'Required custom property is missing. : {prop}')

            return {'CANCELLED'}

        context.props_body[prop] = int(self.type)

        # update custom property
        context.props_body.id_data.update_tag()
        context.area.tag_redraw()

        return {'FINISHED'}
