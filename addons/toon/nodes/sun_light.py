from toon.utils import override

from bpy.types import NodeTree

from .base import ToonNodeLight, create_script_node


class ToonNodeSunLight(ToonNodeLight):
    bl_name = 'ToonNodeSunLight'
    bl_label = 'Sun Light'

    @override
    def init_node_tree(self, node_tree: NodeTree):
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
        script = create_script_node(node_tree, 'sun_light')
        node_tree.links.new(rotation.outputs[1], script.inputs[0])
        node_tree.links.new(input.outputs[0], script.inputs[1])

        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(script.outputs[0], output.inputs[0])
