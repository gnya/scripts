import bpy
from . import rules

bl_info = {
    'name': 'Formatter',
    'author': 'gnya',
    'version': (0, 1, 1),
    'blender': (3, 6, 0),
    'description':
        'Change the names, properties, and data structures in the '
        'project data to conform to the rules. (For my personal project.)',
    'category': 'Utility'
}


class VIEW3D_OT_format_project(bpy.types.Operator):
    bl_idname = 'view3d.format_project'
    bl_label = 'Format'
    bl_description = 'Format this project data'
    bl_options = {'UNDO'}

    def execute(self, _):
        print('')
        rules.DefBoneNameRule.fix()
        rules.BBoneNameRule.fix()
        rules.BoneTransformLockRule.fix()
        rules.BoneIKPropsRule.fix()
        rules.SymmetryBoneNameRule.fix()
        rules.SymmetryBoneConstraintRule.fix()
        rules.SymmetryBoneParentRule.fix()
        rules.ConstraintTangetSpaceRule.fix()
        rules.ConstraintOwnerSpaceRule.fix()
        rules.ConstraintNameRule.fix()
        rules.ConstraintPanelRule.fix()
        rules.UnusedCustomShapeRules.fix()
        rules.SymmetryBoneDriverRule.fix()
        rules.ModifierNameRule.fix()
        rules.ModifierPanelRule.fix()

        return {'FINISHED'}


class VIEW3D_PT_format_project(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_format_project'
    bl_label = 'Formatter'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_order = 1

    def draw(self, _):
        layout = self.layout
        layout.operator('view3d.format_project', icon='BRUSH_DATA')


def register():
    bpy.utils.register_class(VIEW3D_OT_format_project)
    bpy.utils.register_class(VIEW3D_PT_format_project)


def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_format_project)
    bpy.utils.unregister_class(VIEW3D_PT_format_project)


if __name__ == '__main__':
    register()
