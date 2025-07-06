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
        bones, missing = utils.ik_fk_bones(context.pose_object, self.bone_group, self.bone_lr)

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
        bones, missing = utils.ik_fk_bones(context.pose_object, self.bone_group, self.bone_lr)

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


class IKParentTypes(bpy.types.PropertyGroup):
    @staticmethod
    def _get_prop(self, prop):
        if self.id_data.pose:
            if 'CTR_properties_body' in self.id_data.pose.bones:
                b = self.id_data.pose.bones['CTR_properties_body']

                if prop in b:
                    return b[prop]

        return 0

    @staticmethod
    def _set_prop(self, prop, value):
        if self.id_data.pose:
            if 'CTR_properties_body' in self.id_data.pose.bones:
                b = self.id_data.pose.bones['CTR_properties_body']

                if prop in b:
                    b[prop] = int(value)

    arm_l: bpy.props.EnumProperty(
        items=[
            ('0', 'IK Parent - Root', ''),  # noqa: F722 F821
            ('1', 'IK Parent - Torso', ''),  # noqa: F722 F821
            ('2', 'IK Parent - Chest', '')  # noqa: F722 F821
        ],
        name='IK Arm Parent L',  # noqa: F722
        options=set(),
        get=lambda self: IKParentTypes._get_prop(self, 'ik_arm_parent.L'),
        set=lambda self, value:  IKParentTypes._set_prop(self, 'ik_arm_parent.L', value)
    )  # type: ignore

    arm_r: bpy.props.EnumProperty(
        items=[
            ('0', 'IK Parent - Root', ''),  # noqa: F722 F821
            ('1', 'IK Parent - Torso', ''),  # noqa: F722 F821
            ('2', 'IK Parent - Chest', '')  # noqa: F722 F821
        ],
        name='IK Arm Parent R',  # noqa: F722
        options=set(),
        get=lambda self: IKParentTypes._get_prop(self, 'ik_arm_parent.R'),
        set=lambda self, value:  IKParentTypes._set_prop(self, 'ik_arm_parent.R', value)
    )  # type: ignore

    leg_l: bpy.props.EnumProperty(
        items=[
            ('0', 'IK Parent - Root', ''),  # noqa: F722 F821
            ('1', 'IK Parent - Torso', ''),  # noqa: F722 F821
            ('2', 'IK Parent - Chest', '')  # noqa: F722 F821
        ],
        name='IK Leg Parent L',  # noqa: F722
        options=set(),
        get=lambda self: IKParentTypes._get_prop(self, 'ik_leg_parent.L'),
        set=lambda self, value:  IKParentTypes._set_prop(self, 'ik_leg_parent.L', value)
    )  # type: ignore

    leg_r: bpy.props.EnumProperty(
        items=[
            ('0', 'IK Parent - Root', ''),  # noqa: F722 F821
            ('1', 'IK Parent - Torso', ''),  # noqa: F722 F821
            ('2', 'IK Parent - Chest', '')  # noqa: F722 F821
        ],
        name='IK Leg Parent R',  # noqa: F722
        options=set(),
        get=lambda self: IKParentTypes._get_prop(self, 'ik_leg_parent.R'),
        set=lambda self, value:  IKParentTypes._set_prop(self, 'ik_leg_parent.R', value)
    )  # type: ignore


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
        armature = context.active_object
        groups = utils.check_ik_fk_bones(bones)
        props = armature.pose.bones["CTR_properties_body"]

        for group, _, lr in groups:
            box = layout.box()

            row = box.row()
            row.alignment = 'CENTER'
            row.label(text=f'{group}.{lr}')

            col = box.column(align=True)

            op_ik_fk = col.operator('view3d.rig_snap_ik_to_fk', icon='SNAP_ON')
            op_ik_fk.bone_group = group
            op_ik_fk.bone_lr = lr

            op_fk_ik = col.operator('view3d.rig_snap_fk_to_ik', icon='SNAP_ON')
            op_fk_ik.bone_group = group
            op_fk_ik.bone_lr = lr

            col.prop(props, f'["fk_{group}.{lr}"]', text='IK - FK')
            col.prop(props, f'["ik_stretch_{group}s"]', text='IK Stretch')
            col.prop(props, f'["ik_{group}_pole_parent.{lr}"]', text='IK Pole Parent')

            split = col.split(align=True, factor=0.7)

            split.prop(armature.rig_addon_props, f'{group}_{lr}'.lower(), toggle=1, text='')
            split.prop(props, f'["ik_{group}_parent.{lr}"]', text='')
