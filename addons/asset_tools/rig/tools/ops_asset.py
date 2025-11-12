import bpy
import os

from .latest_asset import find_latest_asset


class VIEW3D_OT_rig_update_asset(bpy.types.Operator):
    bl_idname = 'view3d.rig_update_asset'
    bl_label = 'Update Asset'
    bl_description = 'Update asset data'
    bl_options = {'UNDO'}

    latest_path: bpy.props.StringProperty(default='')
    latest_file: bpy.props.StringProperty(default='')

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
