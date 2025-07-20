import bpy
import json
import mathutils
import re

from .deps_depth import dependence_depth


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
            bone_depth = dependence_depth(obj)

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


class VIEW3D_OT_rig_show_animated_bones(bpy.types.Operator):
    bl_idname = 'view3d.rig_show_animated_bones'
    bl_label = 'Show animated bones'
    bl_description = 'Show animated bones'
    bl_options = {'UNDO'}

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
        data = obj.data
        animated_bones = set()

        for f in obj.animation_data.action.fcurves:
            m = re.findall(r'CTR_[^"]+', f.data_path)

            if m and m[0] in data.bones:
                animated_bones.add(m[0])

        layers = [False] * 32

        for b in data.bones:
            if not re.match('CTR_.*', b.name):
                continue

            if b.name not in animated_bones:
                b.hide = True

                continue

            b.hide = False

            for i in range(32):
                layers[i] |= b.layers[i]

        for i in range(32):
            data.layers[i] = layers[i]

        return {'FINISHED'}
