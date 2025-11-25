from toon.utils import override

from bpy.props import EnumProperty
from bpy.types import Context, Node, NodeTree, UILayout

from toon.utils import NodeLinkRebinder

from .base import ToonNodeOSL


class ToonNodeVisualize(ToonNodeOSL):
    bl_idname = 'ToonNodeVisualize'
    bl_label = 'Visualize'
    osl_name = 'visualize'

    visualize_types = [
        ('0', 'Shadow ID', ''),
        ('1', 'Transparent ID', ''),
        ('2', 'Shadow Properties', '')
    ]

    def _update_visualize_type(self, context: Context):
        with NodeLinkRebinder(self):
            self.free()
            self.init(context)

    visualize_type: EnumProperty(
        items=visualize_types, name='Visualize Type', default='0',
        update=_update_visualize_type
    )

    @override
    def node_tree_key(self) -> tuple[str, str]:
        name, lib = super().node_tree_key()

        return f'{name}_{self.visualize_type}', lib

    @override
    def init_sockets(self, node_tree: NodeTree):
        node_tree.outputs.new('NodeSocketColor', 'Color')

    @override
    def init_node_tree(self, node_tree: NodeTree, script: Node):
        script.inputs[0].default_value = int(self.visualize_type)
        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(script.outputs[0], output.inputs[0])

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
        layout.prop(self, 'visualize_type', text='')
