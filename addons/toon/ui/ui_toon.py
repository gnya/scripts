from toon.utils import override

from bpy import types
from bpy.types import Context, Panel


def _draw_pass_index_warning(self: Panel, context: Context):
    if (
        context.scene.render.engine == 'CYCLES' and
        context.scene.cycles.shading_system
    ):
        layout = self.layout
        warning_box = layout.box()

        warning_box.label(text='Do not modify the pass index number directly.', icon='ERROR')


class OBJECT_PT_toon(Panel):
    bl_label = 'Toon'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @override
    def draw(self, context: Context):
        layout = self.layout

        if context.object is None:
            return

        settings = context.object.toon_settings

        col = layout.column()
        col.use_property_split = True
        col.prop(settings, 'cast_shadows', text='Cast Shadows')
        col.prop(settings, 'shadow_id', text='Shadow ID')
        col.prop(settings, 'transparent_id', text='Transparent ID')

    @staticmethod
    def register():
        types.OBJECT_PT_relations.append(_draw_pass_index_warning)

    @staticmethod
    def unregister():
        types.OBJECT_PT_relations.remove(_draw_pass_index_warning)


class MATERIAL_PT_toon(Panel):
    bl_label = 'Toon'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    @override
    def draw(self, context: Context):
        layout = self.layout

        if context.object is None or context.material is None:
            return

        object_settings = context.object.toon_settings
        settings = context.material.toon_settings

        col = layout.column()
        col.use_property_split = True

        row = col.row()
        row.prop(settings, 'cast_shadows', text='Cast Shadows')
        row.active = int(object_settings.cast_shadows) == 0

        row = col.row()
        row.prop(settings, 'shadow_id', text='Shadow ID')
        row.active = object_settings.shadow_id == 0

        row = col.row()
        row.prop(settings, 'transparent_id', text='Transparent ID')
        row.active = object_settings.transparent_id == 0

    @staticmethod
    def register():
        types.EEVEE_MATERIAL_PT_viewport_settings.append(_draw_pass_index_warning)

        if hasattr(types, 'CYCLES_MATERIAL_PT_settings'):
            types.CYCLES_MATERIAL_PT_settings.append(_draw_pass_index_warning)

    @staticmethod
    def unregister():
        types.EEVEE_MATERIAL_PT_viewport_settings.remove(_draw_pass_index_warning)

        if hasattr(types, 'CYCLES_MATERIAL_PT_settings'):
            types.CYCLES_MATERIAL_PT_settings.remove(_draw_pass_index_warning)
