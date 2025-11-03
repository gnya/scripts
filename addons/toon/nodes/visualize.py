import bpy

from .base import ToonNodeBase, create_script_node


class ToonNodeVisualize(ToonNodeBase):
    bl_name = 'ToonNodeVisualize'
    bl_label = 'Visualize'

    visualize_types = [
        ('0', 'Shadow ID', ''),
        ('1', 'Transparent ID', ''),
        ('2', 'Shadow Properties', '')
    ]

    def update_visualize_type(self, context):
        script = self.node_tree.nodes['Script']
        script.inputs[0].default_value = int(self.visualize_type)

    visualize_type: bpy.props.EnumProperty(
        name='Visualize Type',  # noqa: F722
        default='0', items=visualize_types, update=update_visualize_type
    )  # type: ignore

    def init_toon_node(self, context, node_tree):
        script = create_script_node(node_tree, 'visualize')
        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.outputs.new('NodeSocketColor', 'Color')
        node_tree.links.new(script.outputs[0], output.inputs[0])

    def draw_buttons(self, context, layout):
        layout.prop(self, 'visualize_type', text='')
