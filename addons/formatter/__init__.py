import bpy
from . import rules


bl_info = {
    'name': 'Formatter',
    'author': 'gnya',
    'version': (0, 2, 10),
    'blender': (3, 6, 0),
    'description':
        'Change the names, properties, and data structures in the '
        'project data to conform to the rules. (For my personal project.)',
    'category': 'Utility'
}


class FormatterReport(bpy.types.PropertyGroup):
    title: bpy.props.StringProperty(default='')
    description: bpy.props.StringProperty(default='')


class VIEW3D_OT_format_project(bpy.types.Operator):
    bl_idname = 'view3d.format_project'
    bl_label = 'Format'
    bl_description = 'Format this project data'
    bl_options = {'UNDO'}

    def execute(self, context):
        logs = context.window_manager.latest_formatter_log_reports
        errors = context.window_manager.latest_formatter_error_reports

        logs.clear()
        errors.clear()

        for rule in rules.__all__:
            r = rule.fix()
            log_reports = r.to_list('LOG')
            error_reports = r.to_list('ERROR')

            for log in log_reports:
                item = logs.add()
                item.title = log.title
                item.description = log.description

            for error in error_reports:
                item = errors.add()
                item.title = error.title
                item.description = error.description

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

        logs = context.window_manager.latest_formatter_log_reports
        errors = context.window_manager.latest_formatter_error_reports

        if len(logs):
            layout.separator()
            layout.label(text='Log', icon='INFO')

            log_box = layout.box().column(align=True)

            for log in logs:
                log_box.label(text=f'{log.title}')

                if log.description:
                    log_subbox = log_box.box().column(align=True)
                    log_subbox.label(text=f'{log.description}')

        if len(errors):
            layout.separator()
            layout.label(text='Error', icon='ERROR')

            error_box = layout.box().column(align=True)
            error_box.alert = True

            for error in errors:
                error_box.label(text=f'{error.title}')

                if error.description:
                    error_subbox = error_box.box().column(align=True)
                    error_subbox.label(text=f'{error.description}')


def register():
    bpy.utils.register_class(FormatterReport)

    bpy.types.WindowManager.latest_formatter_log_reports = \
        bpy.props.CollectionProperty(type=FormatterReport)
    bpy.types.WindowManager.latest_formatter_error_reports = \
        bpy.props.CollectionProperty(type=FormatterReport)

    bpy.utils.register_class(VIEW3D_OT_format_project)
    bpy.utils.register_class(VIEW3D_PT_format_project)


def unregister():
    bpy.utils.unregister_class(FormatterReport)

    del bpy.types.WindowManager.latest_formatter_log_reports
    del bpy.types.WindowManager.latest_formatter_error_reports

    bpy.utils.unregister_class(VIEW3D_OT_format_project)
    bpy.utils.unregister_class(VIEW3D_PT_format_project)


if __name__ == '__main__':
    register()
