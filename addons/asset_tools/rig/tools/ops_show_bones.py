from __future__ import annotations

import re
from typing import TYPE_CHECKING

import bpy
from bpy.types import Context, Event, Object

if TYPE_CHECKING:
    from bpy._typing.rna_enums import ContextModeItems, OperatorReturnItems


class ShowBonesOperator(bpy.types.Operator):
    bl_options = {"UNDO"}

    only_visible: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll_armature(cls, armature: Object, mode: ContextModeItems) -> bool:
        raise NotImplementedError()

    @classmethod
    def poll(cls, context: Context) -> bool:
        obj = context.active_object

        if not obj or not obj.type == "ARMATURE":
            return False

        return cls.poll_armature(obj, context.mode)

    def target_bones(self, armature: Object) -> set[str]:
        raise NotImplementedError()

    def execute(self, context: Context) -> set[OperatorReturnItems]:
        obj = context.active_object

        if obj is None or obj.data is None:
            return {"CANCELLED"}

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

        return {"FINISHED"}

    def invoke(self, context: Context, event: Event):
        self.only_visible = not event.shift

        return self.execute(context)


class VIEW3D_OT_rig_show_overrided_bones(ShowBonesOperator):
    bl_idname = "view3d.rig_show_overrided_bones"
    bl_label = "Show overrided bones"
    bl_description = "Show overrided bones \n* Shift to show all bones"

    @classmethod
    def poll_armature(cls, armature: Object, mode: ContextModeItems) -> bool:
        if mode != "POSE":
            return False

        if not armature.override_library:
            return False

        return True

    def target_bones(self, armature: Object) -> set[str]:
        target = set()

        for p in armature.override_library.properties:
            if m := re.match(r'^pose.bones\["(CTR_[^"]+)"\][.\[][^\[]+$', p.rna_path):
                target.add(m.group(1))

        return target


class VIEW3D_OT_rig_show_animated_bones(ShowBonesOperator):
    bl_idname = "view3d.rig_show_animated_bones"
    bl_label = "Show animated bones"
    bl_description = "Show animated bones \n* Shift to show all bones"

    @classmethod
    def poll_armature(cls, armature: Object, mode: ContextModeItems) -> bool:
        if mode != "POSE":
            return False

        if not armature.animation_data:
            return False

        if not armature.animation_data.action:
            return False

        return True

    def target_bones(self, armature: Object) -> set[str]:
        target = set()

        if armature.animation_data.action is None:
            return target

        for f in armature.animation_data.action.fcurves:
            if m := re.match(r'^pose.bones\["(CTR_[^"]+)"\]', f.data_path):
                target.add(m.group(1))

        return target


class VIEW3D_OT_rig_show_prefix_bones(ShowBonesOperator):
    bl_idname = "view3d.rig_show_prefix_bones"
    bl_label = "Show prefix bones"
    bl_description = "Show prefix bones \n* Shift to show all bones"

    type: bpy.props.EnumProperty(
        items=[
            ("CTR", "Control Bones", ""),
            ("DEF", "Deform Bones", ""),
            ("MCH", "Mechanical Bones", ""),
            ("CSP", "Custom Shape Bones", ""),
        ],
        translation_context="Operator",
    )

    @classmethod
    def poll_armature(cls, armature: Object, mode: ContextModeItems) -> bool:
        return True

    def target_bones(self, armature: Object) -> set[str]:
        target = set()

        for b in armature.pose.bones:
            if b.name.split("_")[0] == self.type:
                target.add(b.name)

        return target
