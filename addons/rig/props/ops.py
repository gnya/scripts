import bpy
import json
import mathutils
import os
import re

from .deps_depth import calc_dependency_depth
from .latest_asset import find_latest_asset


class VIEW3D_OT_rig_attach_light(bpy.types.Operator):
    bl_idname = 'view3d.rig_attach_light'
    bl_label = 'Attach Light'
    bl_description = 'Attach a light object'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return False

    def execute(self, context):
        return {'FINISHED'}


class VIEW3D_OT_rig_update_asset(bpy.types.Operator):
    bl_idname = 'view3d.rig_update_asset'
    bl_label = 'Update Asset'
    bl_description = 'Update asset data'
    bl_options = {'UNDO'}

    latest_path: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722
    latest_file: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if not obj or not obj.override_library:
            return False

        return True

    def execute(self, context):
        obj = context.active_object
        lib = obj.override_library.reference.library

        lib.filepath = bpy.path.relpath(self.latest_path)
        lib.reload()

        return {'FINISHED'}

    def invoke(self, context, event):
        obj = context.active_object
        wm = context.window_manager

        lib = obj.override_library.reference.library
        blend_path = bpy.path.abspath(lib.filepath)
        blend_dir = os.path.dirname(blend_path)
        blend_file = os.path.basename(blend_path)

        self.latest_path, self.latest_file = find_latest_asset(blend_dir)
        self.latest_path = bpy.path.relpath(self.latest_path)

        if blend_file != self.latest_file:
            return wm.invoke_confirm(self, event)
        else:
            self.report({'INFO'}, 'This asset is the latest.')

            return {'CANCELLED'}


class VIEW3D_OT_rig_copy_pose(bpy.types.Operator):
    bl_idname = 'view3d.rig_copy_pose'
    bl_label = 'Copy Pose (World Space)'
    bl_description = 'Copy pose (world space)'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if not obj or not obj.type == 'ARMATURE':
            return False

        if context.mode != 'POSE':
            return False

        return True

    def execute(self, context):
        obj = context.active_object
        bones = obj.pose.bones

        data = {}

        for b in bones:
            if not re.match('CTR_.*', b.name):
                continue

            if not b.bone.select:
                continue

            m = obj.convert_space(
                pose_bone=b, matrix=b.matrix,
                from_space='POSE', to_space='WORLD'
            )

            data[b.name] = {
                'space': 'WORLD',
                'matrix': [list(r) for r in m.row]
            }

        context.window_manager.clipboard = json.dumps(data)

        return {'FINISHED'}


class VIEW3D_OT_rig_paste_pose(bpy.types.Operator):
    bl_idname = 'view3d.rig_paste_pose'
    bl_label = 'Copy Pose (World Space)'
    bl_description = 'Paste pose (world space)'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if not obj or not obj.type == 'ARMATURE':
            return False

        if context.mode != 'POSE':
            return False

        return True

    def execute(self, context):
        try:
            data = json.loads(context.window_manager.clipboard)
        except json.decoder.JSONDecodeError:
            return {'CANCELLED'}
        else:
            obj = context.active_object
            bones = obj.pose.bones
            bone_depth = calc_dependency_depth(obj)

            # Create a dict of bones with depth as a key.
            depth_bone = {}

            for bone in data.keys():
                if bone not in bones:
                    continue

                depth = bone_depth[bone]

                if depth not in depth_bone:
                    depth_bone[depth] = []

                depth_bone[depth].append(bone)

            # Apply the poses in order from the shallowest bone in depth.
            sorted_depth = sorted(depth_bone.keys(), key=lambda d: d)

            if -1 in sorted_depth:
                self.report({'ERROR'}, 'Dependency cycle detected.')

                return {'CANCELLED'}

            for depth in sorted_depth:
                for bone in depth_bone[depth]:
                    b = bones[bone]
                    m = mathutils.Matrix(data[bone]['matrix'])

                    b.matrix = obj.convert_space(
                        pose_bone=b, matrix=m,
                        from_space=data[bone]['space'], to_space='POSE'
                    )

                context.view_layer.update()

        return {'FINISHED'}


class VIEW3D_OT_rig_copy_whole_pose(bpy.types.Operator):
    bl_idname = 'view3d.rig_copy_whole_pose'
    bl_label = 'Copy Whole Pose'
    bl_description = 'Copy pose including unselected bones'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if not obj or not obj.type == 'ARMATURE':
            return False

        if context.mode != 'POSE':
            return False

        return True

    def execute(self, context):
        obj = context.active_object
        bones = obj.pose.bones
        selection = {}
        layers = [False] * 32

        for b in bones:
            selection[b.name] = b.bone.select
            b.bone.select = bool(re.match('CTR_.*', b.name))

        for i in range(32):
            layers[i] = obj.data.layers[i]
            obj.data.layers[i] = True

        bpy.ops.pose.copy()

        for b in bones:
            b.bone.select = selection[b.name]

        for i in range(32):
            obj.data.layers[i] = layers[i]

        return {'FINISHED'}


class VIEW3D_OT_rig_show_overrided_bones(bpy.types.Operator):
    bl_idname = 'view3d.rig_show_overrided_bones'
    bl_label = 'Show overrided bones'
    bl_description = 'Show overrided bones \n* Shift to show all bones'
    bl_options = {'UNDO'}

    only_visible: bpy.props.BoolProperty(default=True)  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if not obj or not obj.type == 'ARMATURE':
            return False

        if context.mode != 'POSE':
            return False

        if not obj.override_library:
            return False

        return True

    def execute(self, context):
        obj = context.active_object
        bones = obj.pose.bones
        overrided_bones = set()

        for p in obj.override_library.properties:
            if m := re.match(r'^pose.bones\["(CTR_[^"]+)"\].[^.]+$', p.rna_path):
                overrided_bones.add(m.group(1))

        layers = [False] * 32

        if self.only_visible:
            layers = obj.data.layers
        else:
            for b in bones:
                if not re.match('CTR_.*', b.name):
                    continue

                if b.name in overrided_bones:
                    for i in range(32):
                        layers[i] |= b.bone.layers[i]

        for b in bones:
            if not re.match('CTR_.*', b.name):
                continue

            if not any([(b.bone.layers[i] and layers[i]) for i in range(32)]):
                continue

            b.bone.hide = b.name not in overrided_bones

        for i in range(32):
            obj.data.layers[i] = layers[i]

        return {'FINISHED'}

    def invoke(self, context, event):
        self.only_visible = not event.shift

        return self.execute(context)


class VIEW3D_OT_rig_show_animated_bones(bpy.types.Operator):
    bl_idname = 'view3d.rig_show_animated_bones'
    bl_label = 'Show animated bones'
    bl_description = 'Show animated bones \n* Shift to show all bones'
    bl_options = {'UNDO'}

    only_visible: bpy.props.BoolProperty(default=True)  # type: ignore

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if not obj or not obj.type == 'ARMATURE':
            return False

        if context.mode != 'POSE':
            return False

        if not obj.animation_data or not obj.animation_data.action:
            return False

        return True

    def execute(self, context):
        obj = context.active_object
        bones = obj.pose.bones
        animated_bones = set()

        for f in obj.animation_data.action.fcurves:
            if m := re.match(r'^pose.bones\["(CTR_[^"]+)"\]', f.data_path):
                animated_bones.add(m.group(1))

        layers = [False] * 32

        if self.only_visible:
            layers = obj.data.layers
        else:
            for b in bones:
                if not re.match('CTR_.*', b.name):
                    continue

                if b.name in animated_bones:
                    for i in range(32):
                        layers[i] |= b.bone.layers[i]

        for b in bones:
            if not re.match('CTR_.*', b.name):
                continue

            if not any([(b.bone.layers[i] and layers[i]) for i in range(32)]):
                continue

            b.bone.hide = b.name not in animated_bones

        for i in range(32):
            obj.data.layers[i] = layers[i]

        return {'FINISHED'}

    def invoke(self, context, event):
        self.only_visible = not event.shift

        return self.execute(context)
