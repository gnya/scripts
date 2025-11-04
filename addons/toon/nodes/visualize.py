from bpy.props import EnumProperty
from bpy.types import Context

from .base import ToonNodeBase, create_script_node


class ToonNodeVisualize(ToonNodeBase):
    bl_name = 'ToonNodeVisualize'
    bl_label = 'Visualize'
    copy_node_tree = True

    visualize_types = [
        ('0', 'Shadow ID', ''),
        ('1', 'Transparent ID', ''),
        ('2', 'Shadow Properties', '')
    ]

    def update_visualize_type(self, context: Context):
        script = self.node_tree.nodes['Script']
        script.inputs[0].default_value = int(self.visualize_type)

    visualize_type: EnumProperty(
        name='Visualize Type',  # noqa: F722
        default='0', items=visualize_types,
        update=lambda self, context: self.update_visualize_type(context)
    )  # type: ignore

    def init_toon_node(self, context, node_tree):
        node_tree.outputs.new('NodeSocketColor', 'Color')

        script = create_script_node(node_tree, 'visualize')
        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(script.outputs[0], output.inputs[0])

    def draw_buttons(self, context, layout):
        layout.prop(self, 'visualize_type', text='')
