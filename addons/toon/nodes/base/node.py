from toon.utils import override

import bpy

from bpy.props import BoolProperty
from bpy.types import Context, NodeTree, ShaderNodeCustomGroup, UILayout

from toon.ops import NODE_OT_toon_node_reload_all
from toon.utils import NodeLinkRebinder


class ToonNode(ShaderNodeCustomGroup):
    pass


class ToonNodeGroup(ToonNode):
    node_ready: BoolProperty(default=False)

    def node_tree_key(self) -> tuple[str, str]:
        return f'.{self.bl_idname}', ''

    def new_node_tree(self, name: str) -> tuple[NodeTree, bool]:
        raise NotImplementedError()

    def get_node_tree(self) -> tuple[NodeTree | None, bool]:
        name, lib = self.node_tree_key()

        if not name:
            return None, False
        elif not lib and name in bpy.data.node_groups:
            return bpy.data.node_groups[name], True
        elif (name, lib) in bpy.data.node_groups:
            return bpy.data.node_groups[name, lib], True
        else:
            return self.new_node_tree(name)

    def reload(self):
        if self.node_tree is None:
            return

        if not self.node_tree.name.startswith('.ToonNodeObsolete'):
            self.node_tree.name = f'.ToonNodeObsolete{self.node_tree.name}'

        with NodeLinkRebinder(self):
            self.free()
            self.init(None)

    @override
    def init(self, context: Context):
        self.node_tree = None
        self.node_tree, self.node_ready = self.get_node_tree()

    @override
    def free(self):
        node_tree = self.node_tree
        self.node_tree, self.node_ready = None, False

        if node_tree is not None and node_tree.users == 0:
            bpy.data.node_groups.remove(node_tree)

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
        if not self.node_ready:
            layout.operator(
                NODE_OT_toon_node_reload_all.bl_idname,
                text='Reload', icon='FILE_REFRESH'
            )
