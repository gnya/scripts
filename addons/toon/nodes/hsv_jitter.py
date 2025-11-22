from toon.utils import override

from bpy.types import NodeTree

from .base import ToonNode, create_script_node


class ToonNodeHSVJitter(ToonNode):
    bl_name = 'ToonNodeHSVJitter'
    bl_label = 'HSV Jitter'

    @override
    def init_node_tree(self, node_tree: NodeTree):
        i = node_tree.inputs.new('NodeSocketFloat', 'Seed')
        i.default_value = 0.0
        i.min_value = float('-inf')
        i.max_value = float('inf')

        i = node_tree.inputs.new('NodeSocketFloat', 'Hue Jitter')
        i.default_value = 0.0
        i.min_value = 0.0
        i.max_value = 1.0

        i = node_tree.inputs.new('NodeSocketFloat', 'Saturation Jitter')
        i.default_value = 0.0
        i.min_value = 0.0
        i.max_value = 1.0

        i = node_tree.inputs.new('NodeSocketFloat', 'Value Jitter')
        i.default_value = 0.0
        i.min_value = 0.0
        i.max_value = 1.0

        i = node_tree.inputs.new('NodeSocketFloat', 'Fac Jitter')
        i.default_value = 0.0
        i.min_value = 0.0
        i.max_value = 1.0

        i = node_tree.inputs.new('NodeSocketFloat', 'Hue')
        i.default_value = 0.5
        i.min_value = 0.0
        i.max_value = 1.0

        i = node_tree.inputs.new('NodeSocketFloat', 'Saturation')
        i.default_value = 1.0
        i.min_value = 0.0
        i.max_value = 2.0

        i = node_tree.inputs.new('NodeSocketFloat', 'Value')
        i.default_value = 1.0
        i.min_value = 0.0
        i.max_value = 2.0

        i = node_tree.inputs.new('NodeSocketFloatFactor', 'Fac')
        i.default_value = 1.0
        i.min_value = 0.0
        i.max_value = 1.0

        i = node_tree.inputs.new('NodeSocketColor', 'Color')
        i.default_value = (1.0, 1.0, 1.0, 1.0)

        node_tree.outputs.new('NodeSocketColor', 'Color')

        input = node_tree.nodes.new('NodeGroupInput')
        script = create_script_node(node_tree, 'hsv_jitter')
        node_tree.links.new(input.outputs[0], script.inputs[0])
        node_tree.links.new(input.outputs[1], script.inputs[1])
        node_tree.links.new(input.outputs[2], script.inputs[2])
        node_tree.links.new(input.outputs[3], script.inputs[3])
        node_tree.links.new(input.outputs[4], script.inputs[4])
        node_tree.links.new(input.outputs[5], script.inputs[5])
        node_tree.links.new(input.outputs[6], script.inputs[6])
        node_tree.links.new(input.outputs[7], script.inputs[7])
        node_tree.links.new(input.outputs[8], script.inputs[8])

        hsv = node_tree.nodes.new('ShaderNodeHueSaturation')
        node_tree.links.new(script.outputs[0], hsv.inputs[0])
        node_tree.links.new(script.outputs[1], hsv.inputs[1])
        node_tree.links.new(script.outputs[2], hsv.inputs[2])
        node_tree.links.new(script.outputs[3], hsv.inputs[3])
        node_tree.links.new(input.outputs[9], hsv.inputs[4])

        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(hsv.outputs[0], output.inputs[0])
