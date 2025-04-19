import bpy
from . import rules

bl_info = {
    'name': 'Formatter',
    'author': 'gnya',
    'version': (0, 2, 4),
    'blender': (3, 6, 0),
    'description':
        'Change the names, properties, and data structures in the '
        'project data to conform to the rules. (For my personal project.)',
    'category': 'Utility'
}


class FixLogInfo(bpy.types.PropertyGroup):
    text: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722


class FixErrorInfo(bpy.types.PropertyGroup):
    text: bpy.props.StringProperty(default='')  # type: ignore # noqa: F722


class VIEW3D_OT_format_project(bpy.types.Operator):
    bl_idname = 'view3d.format_project'
    bl_label = 'Format'
    bl_description = 'Format this project data'
    bl_options = {'UNDO'}

    def execute(self, context):
        logs = context.window_manager.latest_formatter_fix_logs
        errors = context.window_manager.latest_formatter_fix_errors

        logs.clear()
        errors.clear()

        for rule in rules.__all__:
            r = rule.fix()

            for log in r.logs:
                item = logs.add()
                item.text = log

            for error in r.errors:
                item = errors.add()
                item.text = error

        return {'FINISHED'}


class VIEW3D_PT_format_project(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_format_project'
    bl_label = 'Formatter'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        layout.operator('view3d.format_project', icon='BRUSH_DATA')

        logs = context.window_manager.latest_formatter_fix_logs
        errors = context.window_manager.latest_formatter_fix_errors

        if len(logs):
            layout.separator()
            layout.label(text='Log', icon='INFO')

            log_box = layout.box().column(align=True)

            for log in logs:
                log_box.label(text=f'{log.text}')

        if len(errors):
            layout.separator()
            layout.label(text='Error', icon='ERROR')

            error_log = layout.box().column(align=True)
            error_log.alert = True

            for error in errors:
                error_log.label(text=f'{error.text}')


def register():
    bpy.utils.register_class(FixLogInfo)
    bpy.utils.register_class(FixErrorInfo)

    bpy.types.WindowManager.latest_formatter_fix_logs = \
        bpy.props.CollectionProperty(type=FixLogInfo)
    bpy.types.WindowManager.latest_formatter_fix_errors = \
        bpy.props.CollectionProperty(type=FixErrorInfo)

    bpy.utils.register_class(VIEW3D_OT_format_project)
    bpy.utils.register_class(VIEW3D_PT_format_project)


def unregister():
    bpy.utils.unregister_class(FixLogInfo)
    bpy.utils.unregister_class(FixErrorInfo)

    del bpy.types.WindowManager.latest_formatter_fix_logs
    del bpy.types.WindowManager.latest_formatter_fix_errors

    bpy.utils.unregister_class(VIEW3D_OT_format_project)
    bpy.utils.unregister_class(VIEW3D_PT_format_project)


if __name__ == '__main__':
    register()
