from toon.utils import override

from bpy.types import NodeTree

from .base import ToonNode, create_script_node


class ToonNodeMatCap(ToonNode):
    bl_name = 'ToonNodeMatCap'
    bl_label = 'MatCap'

    @override
    def init_node_tree(self, node_tree: NodeTree):
        node_tree.outputs.new('NodeSocketVector', 'UV')

        script = create_script_node(node_tree, 'matcap')
        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(script.outputs[0], output.inputs[0])
