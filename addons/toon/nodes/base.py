import bpy

from bpy.types import Context, NodeTree, Object, ShaderNodeCustomGroup
from bpy.props import PointerProperty

from toon.shaders import script_abs_path


def create_script_node(node_tree: NodeTree, script_name: str):
    script = node_tree.nodes.new('ShaderNodeScript')
    script.mode = 'EXTERNAL'
    script.filepath = script_abs_path(script_name)

    return script


class ToonNodeBase(ShaderNodeCustomGroup):
    # Set this to True if you want to duplicate each node tree individually.
    copy_node_tree = False

    def init_toon_node(self, context: Context, node_tree: NodeTree):
        raise NotImplementedError()

    def init(self, context):
        name = f'.{self.bl_name}'
        node_tree = bpy.data.node_groups.get(name)

        if not node_tree or self.copy_node_tree:
            node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')
            self.init_toon_node(context, node_tree)

        # Assignment to `self.node_tree` must always be done last.
        self.node_tree = node_tree

    def copy(self, node):
        if self.copy_node_tree:
            self.node_tree = node.node_tree.copy()

    def free(self):
        if self.node_tree.users == 1:
            bpy.data.node_groups.remove(self.node_tree)


class ToonNodeLightBase(ToonNodeBase):
    copy_node_tree = True

    def update_object(self, context: Context):
        raise NotImplementedError()

    object: PointerProperty(
        name='Object',  # noqa: F821
        type=Object,
        update=lambda self, context: self.update_object(context)
    )  # type: ignore

    def draw_buttons(self, context, layout):
        layout.prop(self, 'object', text='Object')
