from toon.utils import override

import bpy

from bpy.types import Context, NodeTree, ShaderNodeCustomGroup


class ToonNode(ShaderNodeCustomGroup):
    pass


class ToonNodeGroup(ToonNode):
    def node_tree_key(self) -> tuple[str, str]:
        return f'.{self.bl_idname}', ''

    def new_node_tree(self, name: str) -> NodeTree:
        raise NotImplementedError()

    def get_node_tree(self) -> NodeTree | None:
        name, lib = self.node_tree_key()

        if not name:
            return None
        elif not lib and name in bpy.data.node_groups:
            return bpy.data.node_groups[name]
        elif (name, lib) in bpy.data.node_groups:
            return bpy.data.node_groups[name, lib]
        else:
            return self.new_node_tree(name)

    @override
    def init(self, context: Context):
        self.node_tree = None
        self.node_tree = self.get_node_tree()

    @override
    def free(self):
        node_tree = self.node_tree
        self.node_tree = None

        if node_tree is not None and node_tree.users == 0:
            bpy.data.node_groups.remove(node_tree)
