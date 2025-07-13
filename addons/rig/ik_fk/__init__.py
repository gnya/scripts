import bpy
from . import utils


class VIEW3D_OT_rig_snap_ik_to_fk(bpy.types.Operator):
    bl_idname = 'view3d.rig_snap_ik_to_fk'
    bl_label = 'IK → FK'
    bl_description = 'Snap IK to FK'
    bl_options = {'UNDO'}

    bone_group: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722
    bone_lr: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722

    def execute(self, context):
        bones, missing = utils.ik_fk_bones(context.snap_target, self.bone_group, self.bone_lr)

        if not bones:
            self.report({'ERROR'}, 'Required ik/fk bones not found.')

            return {'CANCELLED'}
        elif missing:
            self.report({'ERROR'}, f'Required ik/fk bones are missing. : {missing}')

            return {'CANCELLED'}

        if self.bone_group == 'arm':
            utils.snap_arm_ik2fk(bones)
        elif self.bone_group == 'leg':
            utils.snap_leg_ik2fk(bones)

        return {'FINISHED'}


class VIEW3D_OT_rig_snap_fk_to_ik(bpy.types.Operator):
    bl_idname = 'view3d.rig_snap_fk_to_ik'
    bl_label = 'FK → IK'
    bl_description = 'Snap FK to IK'
    bl_options = {'UNDO'}

    bone_group: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722
    bone_lr: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722

    def execute(self, context):
        bones, missing = utils.ik_fk_bones(context.snap_target, self.bone_group, self.bone_lr)

        if not bones:
            self.report({'ERROR'}, 'Required ik/fk bones not found.')

            return {'CANCELLED'}
        elif missing:
            self.report({'ERROR'}, f'Required ik/fk bones are missing. : {missing}')

            return {'CANCELLED'}

        if self.bone_group == 'arm':
            utils.snap_arm_fk2ik(bones)
        elif self.bone_group == 'leg':
            utils.snap_leg_fk2ik(bones)

        return {'FINISHED'}


class VIEW3D_OT_rig_set_ik_parent(bpy.types.Operator):
    bl_idname = 'view3d.rig_set_ik_parent'
    bl_label = 'IK Parent'
    bl_description = 'Set IK Controller\'s parent'
    bl_options = {'UNDO'}

    prop: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722
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

        if self.prop not in context.props_body:
            self.report({'ERROR'}, f'Required custom property is missing. : {self.prop}')

            return {'CANCELLED'}

        context.props_body[self.prop] = int(self.type)

        return {'FINISHED'}


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

        groups = utils.check_ik_fk_bones(bones)

        return True if groups else False

    def draw(self, context):
        layout = self.layout

        bones = context.selected_pose_bones
        groups = utils.check_ik_fk_bones(bones)
        groups = sorted(list(groups), key=lambda g: g[0].name + g[1] + g[3])

        for obj, group, _, lr in groups:
            props = obj.pose.bones["CTR_properties_body"]

            box = layout.box()
            box.context_pointer_set(name='snap_target', data=obj)
            box.context_pointer_set(name='props_body', data=props)

            row = box.row()
            row.alignment = 'CENTER'
            row.label(text=f'{group}.{lr} ({obj.name})', translate=False)

            col = box.column(align=True)

            op = col.operator('view3d.rig_snap_ik_to_fk', translate=False, icon='SNAP_ON')
            op.bone_group = group
            op.bone_lr = lr

            op = col.operator('view3d.rig_snap_fk_to_ik', translate=False, icon='SNAP_ON')
            op.bone_group = group
            op.bone_lr = lr

            col.prop(props, f'["fk_{group}.{lr}"]', text='IK - FK', translate=False)
            col.prop(props, f'["ik_stretch_{group}s"]', text='IK Stretch', translate=False)
            col.prop(
                props, f'["ik_{group}_pole_parent.{lr}"]', text='IK Pole Parent', translate=False)

            parent = ''
            prop = f'ik_{group}_parent.{lr}'

            match props[prop]:
                case 0:
                    parent = 'Root'
                case 1:
                    parent = 'Torso'
                case 2:
                    parent = 'Chest'

            split = col.split(align=True, factor=0.7)
            op = split.operator_menu_enum(
                'view3d.rig_set_ik_parent', 'type', text=f'IK Parent ({parent})', translate=False)
            op.prop = prop
            split.prop(props, f'["{prop}"]', text='')
