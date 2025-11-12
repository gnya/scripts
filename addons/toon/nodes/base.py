import bpy

from bpy.types import (
    Context, Node, NodeTree, Object, ShaderNodeCustomGroup, UILayout
)
from bpy.props import PointerProperty, StringProperty

from toon.shaders import script_abs_path
from toon.utils import override


def create_script_node(node_tree: NodeTree, script_name: str) -> Node:
    script = node_tree.nodes.new('ShaderNodeScript')
    script.mode = 'EXTERNAL'
    script.filepath = script_abs_path(script_name)

    return script


class ToonNode(ShaderNodeCustomGroup):
    def node_tree_name(self) -> str:
        return self.bl_name

    def init_toon_node(self, context: Context, node_tree: NodeTree):
        pass

    @override
    def init(self, context: Context):
        name = self.node_tree_name()

        if not name:
            return

        name = f'.{name}'
        node_tree = bpy.data.node_groups.get(name)

        if node_tree is None:
            node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')
            self.init_toon_node(context, node_tree)

        # Assignment to `self.node_tree` must always be done last.
        self.node_tree = node_tree

    @override
    def free(self):
        node_tree = self.node_tree

        if node_tree is not None and node_tree.users == 1:
            bpy.data.node_groups.remove(node_tree)


class ToonNodeLight(ToonNode):
    last_object_name: StringProperty(default='')

    def _update_object(self, context: Context):
        self.free()
        self.init(context)

        self.last_object_name = self.object.name if self.object else ''

    object: PointerProperty(
        name='Object', type=Object,
        update=_update_object
    )

    @override
    def node_tree_name(self) -> str:
        name = super().node_tree_name()

        return f'{name}_{self.object.name}' if self.object else name

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
        if self.object and self.object.name != self.last_object_name:
            layout.alert = True

        layout.prop(self, 'object', text='Object')
