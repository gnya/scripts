from toon.utils import override

from bpy.types import Node, NodeTree

from .base import ToonNodeOSLLight


class ToonNodeLightArea(ToonNodeOSLLight):
    bl_idname = 'ToonNodeLightArea'
    bl_label = 'Area Light'
    osl_name = 'area_light'

    @override
    def init_sockets(self, node_tree: NodeTree):
        i = node_tree.inputs.new('NodeSocketFloat', 'Energy')
        i.default_value = 1.0
        i.min_value = 0.0
        i.max_value = float('inf')

        i = node_tree.inputs.new('NodeSocketFloat', 'Distance')
        i.default_value = 1.0
        i.min_value = 0.0
        i.max_value = float('inf')

        i = node_tree.inputs.new('NodeSocketFloat', 'Width')
        i.default_value = 1.0
        i.min_value = 0.0
        i.max_value = float('inf')

        i = node_tree.inputs.new('NodeSocketFloat', 'Height')
        i.default_value = 1.0
        i.min_value = 0.0
        i.max_value = float('inf')

        node_tree.outputs.new('NodeSocketVector', 'Light')
        node_tree.outputs.new('NodeSocketVector', 'UV')

    @override
    def init_node_tree(self, node_tree: NodeTree, script: Node):
        location = self.new_attr_node(node_tree, 'location')
        rotation = self.new_attr_node(node_tree, 'rotation_euler')
        input = node_tree.nodes.new('NodeGroupInput')
        node_tree.links.new(location.outputs[1], script.inputs[0])
        node_tree.links.new(rotation.outputs[1], script.inputs[1])
        node_tree.links.new(input.outputs[0], script.inputs[2])
        node_tree.links.new(input.outputs[1], script.inputs[3])
        node_tree.links.new(input.outputs[2], script.inputs[4])
        node_tree.links.new(input.outputs[3], script.inputs[5])

        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(script.outputs[0], output.inputs[0])
        node_tree.links.new(script.outputs[1], output.inputs[1])
