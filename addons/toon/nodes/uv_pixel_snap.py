from toon.utils import override

from bpy.types import Node, NodeTree

from .base import ToonNodeOSL


class ToonNodeUVPixelSnap(ToonNodeOSL):
    bl_name = 'ToonNodeUVPixelSnap'
    bl_label = 'UV Pixel Snap'
    osl_name = 'uv_pixel_snap'

    @override
    def init_node_tree(self, node_tree: NodeTree, script: Node):
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
        node_tree.links.new(input.outputs[0], script.inputs[0])
        node_tree.links.new(input.outputs[1], script.inputs[1])
        node_tree.links.new(input.outputs[2], script.inputs[2])

        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(script.outputs[0], output.inputs[0])
