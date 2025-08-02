import bpy
import re


class ShowBonesOperator(bpy.types.Operator):
    bl_options = {'UNDO'}

    only_visible: bpy.props.BoolProperty(default=True)  # type: ignore

    @classmethod
    def poll_armature(cls, armature):
        raise NotImplementedError()

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if not obj or not obj.type == 'ARMATURE':
            return False

        if context.mode != 'POSE':
            return False

        return cls.poll_armature(obj)

    def target_bones(self, armature):
        raise NotImplementedError()

    def execute(self, context):
        obj = context.active_object
        bones = obj.pose.bones
        target_bones = self.target_bones(obj)

        layers = [False] * 32

        if self.only_visible:
            layers = obj.data.layers
        else:
            for b in bones:
                if b.name in target_bones:
                    for i in range(32):
                        layers[i] |= b.bone.layers[i]

        for b in bones:
            if any([(b.bone.layers[i] and layers[i]) for i in range(32)]):
                b.bone.hide = b.name not in target_bones

        for i in range(32):
            obj.data.layers[i] = layers[i]

        return {'FINISHED'}

    def invoke(self, context, event):
        self.only_visible = not event.shift

        return self.execute(context)


class VIEW3D_OT_rig_show_overrided_bones(ShowBonesOperator):
    bl_idname = 'view3d.rig_show_overrided_bones'
    bl_label = 'Show overrided bones'
    bl_description = 'Show overrided bones \n* Shift to show all bones'

    @classmethod
    def poll_armature(cls, armature):
        if not armature.override_library:
            return False

        return True

    def target_bones(self, armature):
        target = set()

        for p in armature.override_library.properties:
            if m := re.match(r'^pose.bones\["(CTR_[^"]+)"\][.\[][^\[]+$', p.rna_path):
                target.add(m.group(1))

        return target


class VIEW3D_OT_rig_show_animated_bones(ShowBonesOperator):
    bl_idname = 'view3d.rig_show_animated_bones'
    bl_label = 'Show animated bones'
    bl_description = 'Show animated bones \n* Shift to show all bones'

    @classmethod
    def poll_armature(cls, armature):
        if not armature.animation_data or not armature.animation_data.action:
            return False

        return True

    def target_bones(self, armature):
        target = set()

        for f in armature.animation_data.action.fcurves:
            if m := re.match(r'^pose.bones\["(CTR_[^"]+)"\]', f.data_path):
                target.add(m.group(1))

        return target


class VIEW3D_OT_rig_show_prefix_bones(ShowBonesOperator):
    bl_idname = 'view3d.rig_show_prefix_bones'
    bl_label = 'Show prefix bones'
    bl_description = 'Show prefix bones \n* Shift to show all bones'

    type: bpy.props.EnumProperty(
        items=[
            ('CTR', 'Control Bones', ''),  # noqa: F722 F821
            ('DEF', 'Deform Bones', ''),  # noqa: F722 F821
            ('MCH', 'Mechanical Bones', ''),  # noqa: F722 F821
            ('CSP', 'Custom Shape Bones', '')  # noqa: F722 F821
        ],
        translation_context='Operator'  # noqa: F821
    )  # type: ignore

    @classmethod
    def poll_armature(cls, armature):
        return True

    def target_bones(self, armature):
        target = set()

        for b in armature.pose.bones:
            if b.name.split('_')[0] == self.type:
                target.add(b.name)

        return target
