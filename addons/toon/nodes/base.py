from toon.utils import override

import bpy

from bpy.types import (
    Context, Node, NodeTree, Object, ShaderNodeCustomGroup, UILayout
)
from bpy.props import PointerProperty, StringProperty
from nodeitems_utils import NodeCategory

from .shaders import script_path


def create_script_node(node_tree: NodeTree, script_name: str) -> Node:
    script = node_tree.nodes.new('ShaderNodeScript')
    script.mode = 'EXTERNAL'
    script.filepath = script_path(script_name)

    return script


class ToonNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context: Context) -> bool:
        return (
            context.space_data.type == 'NODE_EDITOR' and
            context.space_data.tree_type == 'ShaderNodeTree' and
            context.scene.render.engine == 'CYCLES' and
            context.scene.cycles.shading_system
        )


class ToonNode(ShaderNodeCustomGroup):
    def node_tree_key(self) -> tuple[str, str]:
        return f'.{self.bl_name}', ''

    def init_node_tree(self, node_tree: NodeTree):
        pass

    def get_node_tree(self) -> NodeTree | None:
        name, lib = self.node_tree_key()

        if not name:
            return None
        elif not lib and name in bpy.data.node_groups:
            return bpy.data.node_groups[name]
        elif (name, lib) in bpy.data.node_groups:
            return bpy.data.node_groups[name, lib]
        else:
            node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')
            self.init_node_tree(node_tree)

            return node_tree

    @override
    def init(self, context: Context):
        self.node_tree = None
        self.node_tree = self.get_node_tree()

    @override
    def free(self):
        node_tree = self.node_tree

        if node_tree is not None and node_tree.users == 1:
            bpy.data.node_groups.remove(node_tree)


class ToonNodeLight(ToonNode):
    last_object_name: StringProperty(default='')

    def _poll_object(self, object: Object):
        return object.type in {'LIGHT', 'EMPTY'}

    def _update_object(self, context: Context):
        self.free()
        self.init(context)

        self.last_object_name = self.object.name if self.object else ''

    object: PointerProperty(
        name='Object', type=Object,
        poll=_poll_object,
        update=_update_object
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
