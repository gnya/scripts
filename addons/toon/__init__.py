import bpy

from . import nodes


bl_info = {
    'name': 'Toon',
    'author': 'gnya',
    'version': (0, 0, 2),
    'blender': (3, 6, 0),
    'description':
        'Add shader script wrappers and other features '
        'to make the toon shader easier to use. (For my personal project.)',
    'category': 'Material'
}


class LIGHT_PT_toon(bpy.types.Panel):
    bl_label = 'Toon'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context):
        obj = context.object

        return obj.type == 'LIGHT' or obj.type == 'EMPTY'

    def draw(self, context):
        layout = self.layout

        layout.label(text='Create Light Node Group Button')


class OBJECT_PT_toon(bpy.types.Panel):
    bl_label = 'Toon'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        layout = self.layout

        layout.label(text='Toon Shading Properties')


class MATERIAL_PT_toon(bpy.types.Panel):
    bl_label = 'Toon'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    def draw(self, context):
        layout = self.layout

        layout.label(text='Toon Shading Properties')


def toon_shader_is_available(context):
    return (
        context.scene.render.engine == 'CYCLES' and
        context.scene.cycles.shading_system
    )


def draw_pass_index_warning(self, context):
    if not toon_shader_is_available(context):
        return

    layout = self.layout
    warning_box = layout.box()

    warning_box.label(text='Do not modify the pass index number directly.', icon='ERROR')


def register():
    bpy.utils.register_class(LIGHT_PT_toon)
    bpy.utils.register_class(OBJECT_PT_toon)
    bpy.utils.register_class(MATERIAL_PT_toon)

    bpy.types.OBJECT_PT_relations.append(draw_pass_index_warning)
    bpy.types.EEVEE_MATERIAL_PT_viewport_settings.append(draw_pass_index_warning)
    bpy.types.CYCLES_MATERIAL_PT_settings.append(draw_pass_index_warning)

    nodes.register()


def unregister():
    bpy.utils.unregister_class(LIGHT_PT_toon)
    bpy.utils.unregister_class(OBJECT_PT_toon)
    bpy.utils.unregister_class(MATERIAL_PT_toon)

    bpy.types.OBJECT_PT_relations.remove(draw_pass_index_warning)
    bpy.types.EEVEE_MATERIAL_PT_viewport_settings.remove(draw_pass_index_warning)

    if hasattr(bpy.types, 'CYCLES_MATERIAL_PT_settings'):
        bpy.types.CYCLES_MATERIAL_PT_settings.remove(draw_pass_index_warning)

    nodes.unregister()


if __name__ == '__main__':
    register()
