import bpy


class VIEW3D_OT_color_attach_light(bpy.types.Operator):
    bl_idname = 'view3d.color_attach_light'
    bl_label = 'Attach Light'
    bl_description = 'Attach a light object'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return False

    def execute(self, context):
        return {'FINISHED'}
