import bpy
import os
from nodeitems_utils import NodeItem, register_node_categories, unregister_node_categories
from nodeitems_builtins import ShaderNodeCategory


bl_info = {
    'name': 'Toon',
    'author': 'gnya',
    'version': (0, 0, 1),
    'blender': (3, 6, 0),
    'description':
        'Add shader script wrappers and other features '
        'to make the toon shader easier to use. (For my personal project.)',
    'category': 'Material'
}


def toon_shader_is_available(context):
    return (
        context.scene.render.engine == 'CYCLES' and
        context.scene.cycles.shading_system
    )


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


def draw_pass_index_warning(self, context):
    if not toon_shader_is_available(context):
        return

    layout = self.layout
    warning_box = layout.box()

    warning_box.label(text='Do not modify the pass index number directly.', icon='ERROR')


class ToonNode(bpy.types.ShaderNodeCustomGroup):
    osl_name = ''

    @classmethod
    def init_node_tree(cls, node_tree):
        raise NotImplementedError()

    @classmethod
    def create_script_node(cls, node_tree):
        addon_path = os.path.dirname(os.path.abspath(__file__))
        script = node_tree.nodes.new('ShaderNodeScript')
        script.mode = 'EXTERNAL'
        script.filepath = f'{addon_path}\\shader\\{cls.osl_name}.osl'

        return script

    def init(self, context):
        name = f'.{self.bl_name}'
        node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')
        self.init_node_tree(node_tree)

        # Assignment to `self.node_tree` must always be done last.
        self.node_tree = node_tree

    def copy(self, node):
        self.node_tree = node.node_tree.copy()

    def free(self):
        bpy.data.node_groups.remove(self.node_tree)


class ToonNodeVisualize(ToonNode):
    bl_name = 'ToonNodeVisualize'
    bl_label = 'Visualize'
    osl_name = 'visualize'

    visualize_types = [
        ('0', 'Shadow ID', ''),
        ('1', 'Transparent ID', ''),
        ('2', 'Shadow Properties', '')
    ]

    def update_visualize_type(self, context):
        input = self.node_tree.nodes['Script'].inputs[0]
        input.default_value = int(self.visualize_type)

    visualize_type: bpy.props.EnumProperty(
        default='0', items=visualize_types, name='Type', update=update_visualize_type  # noqa: F821
    )  # type: ignore

    @classmethod
    def init_node_tree(cls, node_tree):
        script = cls.create_script_node(node_tree)
        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.outputs.new('NodeSocketColor', 'Color')
        node_tree.links.new(script.outputs[0], output.inputs[0])

    def draw_buttons(self, context, layout):
        layout.prop(self, 'visualize_type', text='')


class ToonNodeMatCap(ToonNode):
    bl_name = 'ToonNodeMatCap'
    bl_label = 'MatCap'
    osl_name = 'matcap'

    @classmethod
    def init_node_tree(cls, node_tree):
        script = cls.create_script_node(node_tree)
        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.outputs.new('NodeSocketVector', 'UV')
        node_tree.links.new(script.outputs[0], output.inputs[0])


class ToonNodeOutput(ToonNode):
    bl_name = 'ToonNodeOutput'
    bl_label = 'Toon Output'
    osl_name = 'to_closure'

    @classmethod
    def init_node_tree(cls, node_tree):
        i = node_tree.inputs.new('NodeSocketColor', 'Color')
        i.default_value = (1.0, 1.0, 1.0, 1.0)

        i = node_tree.inputs.new('NodeSocketFloatFactor', 'Reflectance')
        i.default_value = 0.0
        i.min_value = 0.0
        i.max_value = 1.0

        i = node_tree.inputs.new('NodeSocketFloat', 'Distance')
        i.default_value = 100.0
        i.min_value = 0.0
        i.max_value = float('inf')

        i = node_tree.inputs.new('NodeSocketFloat', 'Depth')
        i.default_value = 8.0
        i.min_value = 0.0
        i.max_value = float('inf')

        i = node_tree.inputs.new('NodeSocketFloatFactor', 'Transparency')
        i.default_value = 1.0
        i.min_value = 0.0
        i.max_value = 1.0

        input = node_tree.nodes.new('NodeGroupInput')
        script = cls.create_script_node(node_tree)
        node_tree.links.new(input.outputs[0], script.inputs[0])
        node_tree.links.new(input.outputs[1], script.inputs[1])
        node_tree.links.new(input.outputs[2], script.inputs[2])
        node_tree.links.new(input.outputs[3], script.inputs[3])
        node_tree.links.new(input.outputs[4], script.inputs[4])

        render_output = node_tree.nodes.new('ShaderNodeOutputMaterial')
        render_output.target = 'CYCLES'
        node_tree.links.new(script.outputs[0], render_output.inputs[0])

        preview_output = node_tree.nodes.new('ShaderNodeOutputMaterial')
        preview_output.target = 'EEVEE'
        node_tree.links.new(input.outputs[0], preview_output.inputs[0])


class ToonNodeMaterial(ToonNode):
    bl_name = 'ToonNodeMaterial'
    bl_label = 'Material'
    osl_name = 'material'

    @classmethod
    def init_node_tree(cls, node_tree):
        i = node_tree.inputs.new('NodeSocketVector', 'Light')
        i.default_value = (0.0, 0.0, 1.0)
        i.min_value = float('-inf')
        i.max_value = float('inf')
        i.hide_value = True

        i = node_tree.inputs.new('NodeSocketFloatFactor', 'Cutoff')
        i.default_value = 0.05
        i.min_value = 0.0
        i.max_value = 1.0

        i = node_tree.inputs.new('NodeSocketFloatFactor', 'Reflectance')
        i.default_value = 0.5
        i.min_value = 0.0
        i.max_value = 1.0

        i = node_tree.inputs.new('NodeSocketFloat', 'Exponent')
        i.default_value = 10.0
        i.min_value = 0.0
        i.max_value = float('inf')

        node_tree.outputs.new('NodeSocketFloatFactor', 'Diffuse')
        node_tree.outputs.new('NodeSocketFloatFactor', 'Specular')

        input = node_tree.nodes.new('NodeGroupInput')
        script = cls.create_script_node(node_tree)
        node_tree.links.new(input.outputs[0], script.inputs[0])
        node_tree.links.new(input.outputs[1], script.inputs[1])
        node_tree.links.new(input.outputs[2], script.inputs[2])
        node_tree.links.new(input.outputs[3], script.inputs[3])

        preview_mat = node_tree.nodes.new('ShaderNodeBsdfDiffuse')
        preview_mat.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        shader_to_rgb = node_tree.nodes.new('ShaderNodeShaderToRGB')
        node_tree.links.new(preview_mat.outputs[0], shader_to_rgb.inputs[0])

        mix = node_tree.nodes.new('ShaderNodeMix')
        mix.clamp_factor = True
        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(script.outputs[0], mix.inputs[0])
        node_tree.links.new(script.outputs[1], mix.inputs[3])
        node_tree.links.new(script.outputs[2], output.inputs[1])
        node_tree.links.new(shader_to_rgb.outputs[0], mix.inputs[2])
        node_tree.links.new(mix.outputs[0], output.inputs[0])


class ShaderNodeToonCategory(ShaderNodeCategory):
    @classmethod
    def poll(cls, context):
        return (
            super().poll(context) and
            toon_shader_is_available(context)
        )


def register():
    bpy.utils.register_class(LIGHT_PT_toon)
    bpy.utils.register_class(OBJECT_PT_toon)
    bpy.utils.register_class(MATERIAL_PT_toon)

    bpy.types.OBJECT_PT_relations.append(draw_pass_index_warning)

    bpy.types.CYCLES_MATERIAL_PT_settings.append(draw_pass_index_warning)
    bpy.types.EEVEE_MATERIAL_PT_viewport_settings.append(draw_pass_index_warning)

    toon_nodes = [
        NodeItem('ToonNodeVisualize'),
        NodeItem('ToonNodeMatCap'),
        NodeItem('ToonNodeOutput'),
        NodeItem('ToonNodeMaterial')
    ]
    toon_category = [ShaderNodeToonCategory('TOON', 'Toon', items=toon_nodes)]

    bpy.utils.register_class(ToonNodeVisualize)
    bpy.utils.register_class(ToonNodeMatCap)
    bpy.utils.register_class(ToonNodeOutput)
    bpy.utils.register_class(ToonNodeMaterial)
    register_node_categories('TOON_NODES', toon_category)


def unregister():
    bpy.utils.unregister_class(LIGHT_PT_toon)
    bpy.utils.unregister_class(OBJECT_PT_toon)
    bpy.utils.unregister_class(MATERIAL_PT_toon)

    bpy.types.OBJECT_PT_relations.remove(draw_pass_index_warning)

    bpy.types.CYCLES_MATERIAL_PT_settings.remove(draw_pass_index_warning)
    bpy.types.EEVEE_MATERIAL_PT_viewport_settings.remove(draw_pass_index_warning)

    bpy.utils.unregister_class(ToonNodeVisualize)
    bpy.utils.unregister_class(ToonNodeMatCap)
    bpy.utils.unregister_class(ToonNodeOutput)
    bpy.utils.unregister_class(ToonNodeMaterial)
    unregister_node_categories('TOON_NODES')


if __name__ == '__main__':
    register()
