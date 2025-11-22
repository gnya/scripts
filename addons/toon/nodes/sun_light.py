from toon.utils import override

from bpy.types import Node, NodeTree

from .base import ToonNodeOSLLight


class ToonNodeSunLight(ToonNodeOSLLight):
    bl_name = 'ToonNodeSunLight'
    bl_label = 'Sun Light'
    osl_name = 'sun_light'

    @override
    def init_node_tree(self, node_tree: NodeTree, script: Node):
        i = node_tree.inputs.new('NodeSocketFloat', 'Energy')
        i.default_value = 1.0
        i.min_value = 0.0
        i.max_value = float('inf')

        node_tree.outputs.new('NodeSocketVector', 'Light')

        a = f'objects["{self.object.name}"]' if self.object else ''
        rotation = node_tree.nodes.new('ShaderNodeAttribute')
        rotation.name = 'Attribute Rotation'
        rotation.attribute_type = 'VIEW_LAYER'
        rotation.attribute_name = f'{a}.rotation_euler' if a else ''
        input = node_tree.nodes.new('NodeGroupInput')
        node_tree.links.new(rotation.outputs[1], script.inputs[0])
        node_tree.links.new(input.outputs[0], script.inputs[1])

        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(script.outputs[0], output.inputs[0])
