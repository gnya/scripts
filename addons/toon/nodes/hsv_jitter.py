from toon.utils import override

import bpy

from bpy.types import NodeTree

from .base import ToonNodeGroup


class ToonNodeHSVJitter(ToonNodeGroup):
    bl_idname = 'ToonNodeHSVJitter'
    bl_label = 'HSV Jitter'

    @override
    def new_node_tree(self, name: str) -> NodeTree:
        node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')

        i = node_tree.inputs.new('NodeSocketFloat', 'Seed')
        i.default_value = 0.0
        i.min_value = float('-inf')
        i.max_value = float('inf')

        i = node_tree.inputs.new('NodeSocketFloat', 'Hue')
        i.default_value = 0.0
        i.min_value = 0.0
        i.max_value = 1.0

        i = node_tree.inputs.new('NodeSocketFloat', 'Saturation')
        i.default_value = 0.0
        i.min_value = 0.0
        i.max_value = 1.0

        i = node_tree.inputs.new('NodeSocketFloat', 'Value')
        i.default_value = 0.0
        i.min_value = 0.0
        i.max_value = 1.0

        i = node_tree.inputs.new('NodeSocketFloatFactor', 'Fac')
        i.default_value = 1.0
        i.min_value = 0.0
        i.max_value = 1.0

        i = node_tree.inputs.new('NodeSocketColor', 'Color')
        i.default_value = (1.0, 1.0, 1.0, 1.0)

        node_tree.outputs.new('NodeSocketColor', 'Color')

        input = node_tree.nodes.new('NodeGroupInput')

        # float H = hashnoise(Seed + 0.0) * 2.0 - 1.0;
        add_h = node_tree.nodes.new('ShaderNodeMath')
        add_h.operation = 'ADD'
        add_h.inputs[1].default_value = 0.0
        node_tree.links.new(input.outputs[0], add_h.inputs[0])

        noise_h = node_tree.nodes.new('ShaderNodeTexWhiteNoise')
        noise_h.noise_dimensions = '1D'
        node_tree.links.new(add_h.outputs[0], noise_h.inputs[1])

        mul_add_h_1 = node_tree.nodes.new('ShaderNodeMath')
        mul_add_h_1.operation = 'MULTIPLY_ADD'
        mul_add_h_1.inputs[1].default_value = 2.0
        mul_add_h_1.inputs[2].default_value = -1.0
        node_tree.links.new(noise_h.outputs[0], mul_add_h_1.inputs[0])

        # float S = hashnoise(Seed + 1.0) * 2.0 - 1.0;
        add_s = node_tree.nodes.new('ShaderNodeMath')
        add_s.operation = 'ADD'
        add_s.inputs[1].default_value = 1.0
        node_tree.links.new(input.outputs[0], add_s.inputs[0])

        noise_s = node_tree.nodes.new('ShaderNodeTexWhiteNoise')
        noise_s.noise_dimensions = '1D'
        node_tree.links.new(add_s.outputs[0], noise_s.inputs[1])

        mul_add_s_1 = node_tree.nodes.new('ShaderNodeMath')
        mul_add_s_1.operation = 'MULTIPLY_ADD'
        mul_add_s_1.inputs[1].default_value = 2.0
        mul_add_s_1.inputs[2].default_value = -1.0
        node_tree.links.new(noise_s.outputs[0], mul_add_s_1.inputs[0])

        # float V = hashnoise(Seed + 2.0) * 2.0 - 1.0;
        add_v = node_tree.nodes.new('ShaderNodeMath')
        add_v.operation = 'ADD'
        add_v.inputs[1].default_value = 2.0
        node_tree.links.new(input.outputs[0], add_v.inputs[0])

        noise_v = node_tree.nodes.new('ShaderNodeTexWhiteNoise')
        noise_v.noise_dimensions = '1D'
        node_tree.links.new(add_v.outputs[0], noise_v.inputs[1])

        mul_add_v_1 = node_tree.nodes.new('ShaderNodeMath')
        mul_add_v_1.operation = 'MULTIPLY_ADD'
        mul_add_v_1.inputs[1].default_value = 2.0
        mul_add_v_1.inputs[2].default_value = -1.0
        node_tree.links.new(noise_v.outputs[0], mul_add_v_1.inputs[0])

        # Hue = Hue * H + 0.5;
        mul_add_h_2 = node_tree.nodes.new('ShaderNodeMath')
        mul_add_h_2.operation = 'MULTIPLY_ADD'
        mul_add_h_2.inputs[2].default_value = 0.5
        node_tree.links.new(input.outputs[1], mul_add_h_2.inputs[0])
        node_tree.links.new(mul_add_h_1.outputs[0], mul_add_h_2.inputs[1])

        # Saturation = Saturation * S + 1.0;
        mul_add_s_2 = node_tree.nodes.new('ShaderNodeMath')
        mul_add_s_2.operation = 'MULTIPLY_ADD'
        mul_add_s_2.inputs[2].default_value = 1.0
        node_tree.links.new(input.outputs[2], mul_add_s_2.inputs[0])
        node_tree.links.new(mul_add_s_1.outputs[0], mul_add_s_2.inputs[1])

        # Value = Value * V + 1.0;
        mul_add_v_2 = node_tree.nodes.new('ShaderNodeMath')
        mul_add_v_2.operation = 'MULTIPLY_ADD'
        mul_add_v_2.inputs[2].default_value = 1.0
        node_tree.links.new(input.outputs[3], mul_add_v_2.inputs[0])
        node_tree.links.new(mul_add_v_1.outputs[0], mul_add_v_2.inputs[1])

        # ColorOut = node_hsv(Hue, Saturation, Value, Fac, ColorIn)
        hsv = node_tree.nodes.new('ShaderNodeHueSaturation')
        node_tree.links.new(mul_add_h_2.outputs[0], hsv.inputs[0])
        node_tree.links.new(mul_add_s_2.outputs[0], hsv.inputs[1])
        node_tree.links.new(mul_add_v_2.outputs[0], hsv.inputs[2])
        node_tree.links.new(input.outputs[4], hsv.inputs[3])
        node_tree.links.new(input.outputs[5], hsv.inputs[4])

        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(hsv.outputs[0], output.inputs[0])

        return node_tree
