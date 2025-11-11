from toon.utils import override

from .base import ToonNodeLight, create_script_node


class ToonNodePointLight(ToonNodeLight):
    bl_name = 'ToonNodePointLight'
    bl_label = 'Point Light'

    @override
    def init_toon_node(self, context, node_tree):
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
        input = node_tree.nodes.new('NodeGroupInput')
        script = create_script_node(node_tree, 'point_light')
        node_tree.links.new(location.outputs[1], script.inputs[0])
        node_tree.links.new(input.outputs[0], script.inputs[1])
        node_tree.links.new(input.outputs[1], script.inputs[2])

        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(script.outputs[0], output.inputs[0])
