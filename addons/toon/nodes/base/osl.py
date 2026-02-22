from toon.utils import override

import bpy

from bpy.types import Node, NodeTree

from toon.shaders import shader_filepath

from .node import ToonNode


class ToonNodeOSL(ToonNode):
    osl_name = ''

    def _try_load_osl(self, node: Node | None) -> bool:
        if node is None:
            return False

        node.mode = 'EXTERNAL'
        node.filepath = shader_filepath(self.osl_name)

        return len(node.inputs) > 0 or len(node.outputs) > 0

    def init_sockets(self, node_tree: NodeTree):
        pass

    def init_node_tree(self, node_tree: NodeTree, script: Node):
        pass

    @override
    def new_node_tree(self, name: str) -> tuple[NodeTree, bool]:
        node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')
        script = node_tree.nodes.new('ShaderNodeScript')

        self.init_sockets(node_tree)

        if not self._try_load_osl(script):
            return node_tree, False

        self.init_node_tree(node_tree, script)

        return node_tree, True

    @override
    def update(self):
        node_tree = self.node_tree

        if node_tree is None:
            return

        script = node_tree.nodes.get('Script')

        if not self._try_load_osl(script):
            self.node_ready = False
