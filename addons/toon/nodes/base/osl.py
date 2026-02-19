from toon.utils import override

import bpy

from bpy.types import Context, Node, NodeTree, UILayout
from bpy.props import BoolProperty

from toon.shaders import script_filepath

from .node import ToonNodeGroup


class ToonNodeOSL(ToonNodeGroup):
    osl_name = ''

    node_ready: BoolProperty(default=False)

    def _try_load_osl(self, node: Node | None) -> bool:
        if node is None:
            return False

        node.mode = 'EXTERNAL'
        node.filepath = script_filepath(self.osl_name)

        return len(node.inputs) > 0 or len(node.outputs) > 0

    def init_sockets(self, node_tree: NodeTree):
        pass

    def init_node_tree(self, node_tree: NodeTree, script: Node):
        pass

    @override
    def new_node_tree(self, name: str) -> NodeTree:
        node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')
        script = node_tree.nodes.new('ShaderNodeScript')

        self.init_sockets(node_tree)

        if self._try_load_osl(script):
            self.init_node_tree(node_tree, script)
            self.node_ready = True
        else:
            self.node_ready = False

        return node_tree

    @override
    def update(self):
        node_tree = self.node_tree

        if node_tree is None:
            return

        script = node_tree.nodes.get('Script')

        if not self._try_load_osl(script):
            self.node_ready = False

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
        if not self.node_ready:
            layout.label(text='Need reload.', icon='ERROR')
