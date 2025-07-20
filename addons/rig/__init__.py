import bpy
from rig import ik_fk
from rig import props


bl_info = {
    'name': 'Rig',
    'author': 'gnya',
    'version': (0, 1, 11),
    'blender': (3, 6, 0),
    'description':
        'A set of tools to make character rigs easier to use. '
        '(For my personal project.)',
    'category': 'Utility'
}


class VIEW3D_PT_rig_main(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rig_main'
    bl_label = 'Rig'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rig'
    bl_order = 1

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj and (s := obj.name.split('_')):
            col_name = f'{s[0]}_RIGS'

            if col_name not in bpy.data.collections:
                return False

            if bpy.data.collections[col_name] not in obj.users_collection:
                return False

            if obj.type == 'ARMATURE':
                return True

            if obj.type == 'EMPTY':
                return True

        return False

    def draw(self, context):
        pass


def register():
    bpy.utils.register_class(VIEW3D_PT_rig_main)
    props.register()
    ik_fk.register()


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_rig_main)
    props.unregister()
    ik_fk.unregister()


if __name__ == '__main__':
    register()
