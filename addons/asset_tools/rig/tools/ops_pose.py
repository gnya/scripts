import bpy
import json
import mathutils
import re

from .deps_depth import calc_dependency_depth


class VIEW3D_OT_rig_copy_pose(bpy.types.Operator):
    bl_idname = 'view3d.rig_copy_pose'
    bl_label = 'Copy Pose (World Space)'
    bl_description = 'Copy pose (World space)'
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
    bl_description = 'Paste pose (World space)'
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
