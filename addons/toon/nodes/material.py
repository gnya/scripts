from toon.utils import override

from bpy.types import NodeTree

from .base import ToonNode, create_script_node


class ToonNodeMaterial(ToonNode):
    bl_name = 'ToonNodeMaterial'
    bl_label = 'Material'

    @override
    def init_node_tree(self, node_tree: NodeTree):
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
        script = create_script_node(node_tree, 'material')
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
        node_tree.links.new(script.outputs[0], mix.inputs[0])
        node_tree.links.new(shader_to_rgb.outputs[0], mix.inputs[2])
        node_tree.links.new(script.outputs[1], mix.inputs[3])

        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(script.outputs[2], output.inputs[1])
        node_tree.links.new(mix.outputs[0], output.inputs[0])
