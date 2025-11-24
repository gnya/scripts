from toon.utils import override

from bpy.types import Node, NodeTree

from .base import ToonNodeOSLLight


class ToonNodeAreaLight(ToonNodeOSLLight):
    bl_idname = 'ToonNodeAreaLight'
    bl_label = 'Area Light'
    osl_name = 'area_light'

    @override
    def init_node_tree(self, node_tree: NodeTree, script: Node):
        i = node_tree.inputs.new('NodeSocketFloat', 'Energy')
        i.default_value = 1.0
        i.min_value = 0.0
        i.max_value = float('inf')

        i = node_tree.inputs.new('NodeSocketFloat', 'Distance')
        i.default_value = 1.0
        i.min_value = 0.0
        i.max_value = float('inf')

        node_tree.outputs.new('NodeSocketVector', 'Light')

        a = f'objects["{self.object.name}"]' if self.object else ''
        location = node_tree.nodes.new('ShaderNodeAttribute')
        location.name = 'Attribute Location'
        location.attribute_type = 'VIEW_LAYER'
        location.attribute_name = f'{a}.location' if a else ''
        rotation = node_tree.nodes.new('ShaderNodeAttribute')
        rotation.name = 'Attribute Rotation'
        rotation.attribute_type = 'VIEW_LAYER'
        rotation.attribute_name = f'{a}.rotation_euler' if a else ''
        input = node_tree.nodes.new('NodeGroupInput')
        node_tree.links.new(location.outputs[1], script.inputs[0])
        node_tree.links.new(rotation.outputs[1], script.inputs[1])
        node_tree.links.new(input.outputs[0], script.inputs[2])
        node_tree.links.new(input.outputs[1], script.inputs[3])

        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(script.outputs[0], output.inputs[0])
