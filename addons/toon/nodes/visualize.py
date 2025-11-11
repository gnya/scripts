from bpy.props import EnumProperty
from bpy.types import Context, NodeTree, UILayout

from toon.utils import override

from .base import ToonNode, create_script_node


class ToonNodeVisualize(ToonNode):
    bl_name = 'ToonNodeVisualize'
    bl_label = 'Visualize'

    visualize_types = [
        ('0', 'Shadow ID', ''),
        ('1', 'Transparent ID', ''),
        ('2', 'Shadow Properties', '')
    ]

    def _update_visualize_type(self, context: Context):
        self.free()
        self.init(context)

    visualize_type: EnumProperty(
        items=visualize_types, name='Visualize Type', default='0',
        update=_update_visualize_type
    )

    @override
    def node_tree_name(self):
        return f'{super().node_tree_name()}_{self.visualize_type}'

    @override
    def init_toon_node(self, context: Context, node_tree: NodeTree):
        node_tree.outputs.new('NodeSocketColor', 'Color')

        script = create_script_node(node_tree, 'visualize')
        script.inputs[0].default_value = int(self.visualize_type)
        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(script.outputs[0], output.inputs[0])

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
        layout.prop(self, 'visualize_type', text='')
