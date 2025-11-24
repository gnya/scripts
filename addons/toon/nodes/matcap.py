from toon.utils import override

from bpy.types import Node, NodeTree

from .base import ToonNodeOSL


class ToonNodeMatCap(ToonNodeOSL):
    bl_idname = 'ToonNodeMatCap'
    bl_label = 'MatCap'
    osl_name = 'matcap'

    @override
    def init_node_tree(self, node_tree: NodeTree, script: Node):
        node_tree.outputs.new('NodeSocketVector', 'UV')

        output = node_tree.nodes.new('NodeGroupOutput')
        node_tree.links.new(script.outputs[0], output.inputs[0])
