from toon.utils import override

import bpy

from bpy.types import NodeTree

from .base import ToonNodeGroup


class ToonNodeUVPixelSnap(ToonNodeGroup):
    bl_idname = 'ToonNodeUVPixelSnap'
    bl_label = 'UV Pixel Snap'

    @override
    def new_node_tree(self, name: str) -> NodeTree:
        node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')

        i = node_tree.inputs.new('NodeSocketVector', 'UV')
        i.default_value = (0.0, 0.0, 0.0)
        i.min_value = float('-inf')
        i.max_value = float('inf')
        i.hide_value = True

        i = node_tree.inputs.new('NodeSocketFloat', 'Width')
        i.default_value = 1024.0
        i.min_value = 0.0
        i.max_value = float('inf')

        i = node_tree.inputs.new('NodeSocketFloat', 'Height')
        i.default_value = 1024.0
        i.min_value = 0.0
        i.max_value = float('inf')

        node_tree.outputs.new('NodeSocketVector', 'UV')

        input = node_tree.nodes.new('NodeGroupInput')
        xyz = node_tree.nodes.new('ShaderNodeSeparateXYZ')
        node_tree.links.new(input.outputs[0], xyz.inputs[0])

        mul_w = node_tree.nodes.new('ShaderNodeMath')
        mul_w.operation = 'MULTIPLY'
        node_tree.links.new(xyz.outputs[0], mul_w.inputs[0])
        node_tree.links.new(input.outputs[1], mul_w.inputs[1])

        mul_h = node_tree.nodes.new('ShaderNodeMath')
        mul_h.operation = 'MULTIPLY'
        node_tree.links.new(xyz.outputs[1], mul_h.inputs[0])
        node_tree.links.new(input.outputs[2], mul_h.inputs[1])

        floor_w = node_tree.nodes.new('ShaderNodeMath')
        floor_w.operation = 'FLOOR'
        node_tree.links.new(mul_w.outputs[0], floor_w.inputs[0])

        floor_h = node_tree.nodes.new('ShaderNodeMath')
        floor_h.operation = 'FLOOR'
        node_tree.links.new(mul_h.outputs[0], floor_h.inputs[0])

        div_w = node_tree.nodes.new('ShaderNodeMath')
        div_w.operation = 'DIVIDE'
        node_tree.links.new(floor_w.outputs[0], div_w.inputs[0])
        node_tree.links.new(input.outputs[1], div_w.inputs[1])

        div_h = node_tree.nodes.new('ShaderNodeMath')
        div_h.operation = 'DIVIDE'
        node_tree.links.new(floor_h.outputs[0], div_h.inputs[0])
        node_tree.links.new(input.outputs[2], div_h.inputs[1])

        xyz = node_tree.nodes.new('ShaderNodeCombineXYZ')
        node_tree.links.new(div_w.outputs[0], xyz.inputs[0])
        node_tree.links.new(div_h.outputs[0], xyz.inputs[1])

        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(xyz.outputs[0], output.inputs[0])

        return node_tree
