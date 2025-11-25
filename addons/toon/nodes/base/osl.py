from toon.utils import override

import bpy

from bpy.types import (
    Context, Node, NodeTree, Object, UILayout
)
from bpy.props import PointerProperty, StringProperty

from toon.shaders import script_filepath
from toon.utils import NodeLinkRebinder

from .node import ToonNodeGroup


class ToonNodeOSL(ToonNodeGroup):
    osl_name = ''

    def init_sockets(self, node_tree: NodeTree):
        pass

    def init_node_tree(self, node_tree: NodeTree, script: Node):
        pass

    def _try_load_osl(self, node: Node | None) -> bool:
        if node is None:
            return False

        path = script_filepath(self.osl_name)

        if node.filepath == path:
            return True

        node.mode = 'EXTERNAL'
        node.filepath = path

        return len(node.inputs) > 0 or len(node.outputs) > 0

    @override
    def new_node_tree(self, name: str) -> NodeTree:
        node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')
        script = node_tree.nodes.new('ShaderNodeScript')

        self.init_sockets(node_tree)

        if self._try_load_osl(script):
            self.init_node_tree(node_tree, script)

        return node_tree

    @override
    def update(self):
        node_tree = self.node_tree

        if node_tree is None:
            return

        script = node_tree.nodes.get('Script')
        self._try_load_osl(script)


class ToonNodeOSLLight(ToonNodeOSL):
    def _poll_object(self, object: Object):
        return object.type in {'LIGHT', 'EMPTY'}

    def _update_object(self, context: Context):
        with NodeLinkRebinder(self):
            self.free()
            self.init(context)

        self.last_object_name = self.object.name if self.object else ''

    last_object_name: StringProperty(default='')

    object: PointerProperty(
        name='Object', type=Object,
        poll=_poll_object, update=_update_object
    )

    @override
    def node_tree_key(self) -> tuple[str, str]:
        name, lib = super().node_tree_key()

        return f'{name}_{self.object.name}' if self.object else name, lib

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
        if self.object and self.object.name != self.last_object_name:
            layout.alert = True

        layout.prop(self, 'object', text='Object')
