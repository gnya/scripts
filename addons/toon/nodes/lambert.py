from toon.utils import override

from bpy.props import EnumProperty
from bpy.types import Context, Node, NodeTree, UILayout

from toon.utils import NodeLinkRebinder

from .base import ToonNodeOSL


class ToonNodeLambert(ToonNodeOSL):
    bl_name = 'ToonNodeLambert'
    bl_label = 'Lambert'
    osl_name = 'lambert'

    lighting_types = [
        ('0', 'Lambert', ''),
        ('1', 'Half Lambert', '')
    ]

    def _update_visualize_type(self, context: Context):
        with NodeLinkRebinder(self):
            self.free()
            self.init(context)

    lighting_type: EnumProperty(
        items=lighting_types, name='Lighting Type', default='0',
        update=_update_visualize_type
    )

    @override
    def node_tree_key(self) -> tuple[str, str]:
        name, lib = super().node_tree_key()

        return f'{name}_{self.lighting_type}', lib

    @override
    def init_node_tree(self, node_tree: NodeTree, script: Node):
        i = node_tree.inputs.new('NodeSocketVector', 'Light')
        i.default_value = (0.0, 0.0, 1.0)
        i.min_value = float('-inf')
        i.max_value = float('inf')
        i.hide_value = True

        node_tree.outputs.new('NodeSocketFloat', 'Diffuse')

        input = node_tree.nodes.new('NodeGroupInput')
        script.inputs[0].default_value = int(self.lighting_type)
        node_tree.links.new(input.outputs[0], script.inputs[1])

        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(script.outputs[0], output.inputs[0])

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
        layout.prop(self, 'lighting_type', text='')
