import bpy

from bpy.types import Object


def is_rig(obj: Object):
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
