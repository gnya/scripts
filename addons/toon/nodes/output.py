from toon.utils import override

from bpy.types import NodeTree

from .base import ToonNode, create_script_node


class ToonNodeOutput(ToonNode):
    bl_name = 'ToonNodeOutput'
    bl_label = 'Toon Output'

    @override
    def init_node_tree(self, node_tree: NodeTree):
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

        node_tree.outputs.new('NodeSocketShader', 'Shader')

        input = node_tree.nodes.new('NodeGroupInput')
        script = create_script_node(node_tree, 'to_closure')
        node_tree.links.new(input.outputs[0], script.inputs[0])
        node_tree.links.new(input.outputs[1], script.inputs[1])
        node_tree.links.new(input.outputs[2], script.inputs[2])
        node_tree.links.new(input.outputs[3], script.inputs[3])
        node_tree.links.new(input.outputs[4], script.inputs[4])

        mix = node_tree.nodes.new('ShaderNodeMixShader')
        node_tree.links.new(script.outputs[0], mix.inputs[0])
        node_tree.links.new(input.outputs[0], mix.inputs[1])
        node_tree.links.new(script.outputs[1], mix.inputs[2])

        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(mix.outputs[0], output.inputs[0])
