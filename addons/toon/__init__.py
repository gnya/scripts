import bpy

from bpy.props import EnumProperty, IntProperty, PointerProperty
from bpy.types import Context, Panel, PropertyGroup

from . import palette
from . import nodes


bl_info = {
    'name': 'Toon',
    'author': 'gnya',
    'version': (0, 0, 9),
    'blender': (3, 6, 0),
    'description':
        'Add shader script wrappers and other features '
        'to make the toon shader easier to use. (For my personal project.)',
    'category': 'Material'
}


class OBJECT_PT_toon(Panel):
    bl_label = 'Toon'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        layout = self.layout

        settings = context.object.toon_settings

        col = layout.column()
        col.use_property_split = True
        col.prop(settings, 'cast_shadows', text='Cast Shadows')
        col.prop(settings, 'shadow_id', text='Shadow ID')
        col.prop(settings, 'transparent_id', text='Transparent ID')


class MATERIAL_PT_toon(Panel):
    bl_label = 'Toon'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    def draw(self, context):
        layout = self.layout

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


class ToonSettings(PropertyGroup):
    def set_cast_shadows(self, value):
        self.id_data.pass_index = (
            (value << 12) | (self.id_data.pass_index & ~(7 << 12))
        )

    def set_shadow_id(self, value):
        self.id_data.pass_index = (
            (value << 0) | (self.id_data.pass_index & ~(63 << 0))
        )

    def set_transparent_id(self, value):
        self.id_data.pass_index = (
            (value << 6) | (self.id_data.pass_index & ~(63 << 6))
        )

    def get_cast_shadows(self):
        return (self.id_data.pass_index >> 12) & 7

    def get_shadow_id(self):
        return (self.id_data.pass_index >> 0) & 63

    def get_transparent_id(self):
        return (self.id_data.pass_index >> 6) & 63

    shadow_casting_types = [
        ('0', 'Enable', ''),
        ('1', 'Only Front Surface', ''),
        ('2', 'Disable', '')
    ]

    cast_shadows: EnumProperty(
        name='Cast Shadows',
        default='0', items=shadow_casting_types,
        set=set_cast_shadows, get=get_cast_shadows
    )

    shadow_id: IntProperty(
        name='Shadow ID',
        default=0, min=0, max=63,
        set=set_shadow_id, get=get_shadow_id
    )

    transparent_id: IntProperty(
        name='Transparent ID',
        default=0, min=0, max=63,
        set=set_transparent_id, get=get_transparent_id
    )


def draw_pass_index_warning(self, context: Context):
    if (
        context.scene.render.engine == 'CYCLES' and
        context.scene.cycles.shading_system
    ):
        return

    layout = self.layout
    warning_box = layout.box()

    warning_box.label(text='Do not modify the pass index number directly.', icon='ERROR')


def register():
    from bpy.utils import register_class

    register_class(OBJECT_PT_toon)
    register_class(MATERIAL_PT_toon)

    register_class(ToonSettings)

    bpy.types.Object.toon_settings = PointerProperty(type=ToonSettings)
    bpy.types.Material.toon_settings = PointerProperty(type=ToonSettings)

    bpy.types.OBJECT_PT_relations.append(draw_pass_index_warning)
    bpy.types.EEVEE_MATERIAL_PT_viewport_settings.append(draw_pass_index_warning)
    bpy.types.CYCLES_MATERIAL_PT_settings.append(draw_pass_index_warning)

    palette.register()
    nodes.register()


def unregister():
    from bpy.utils import unregister_class

    unregister_class(OBJECT_PT_toon)
    unregister_class(MATERIAL_PT_toon)

    unregister_class(ToonSettings)

    del bpy.types.Object.toon_settings
    del bpy.types.Material.toon_settings

    bpy.types.OBJECT_PT_relations.remove(draw_pass_index_warning)
    bpy.types.EEVEE_MATERIAL_PT_viewport_settings.remove(draw_pass_index_warning)

    if hasattr(bpy.types, 'CYCLES_MATERIAL_PT_settings'):
        bpy.types.CYCLES_MATERIAL_PT_settings.remove(draw_pass_index_warning)

    palette.unregister()
    nodes.unregister()


if __name__ == '__main__':
    register()
