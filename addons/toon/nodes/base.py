import bpy

from bpy.types import Context, NodeTree, Object, ShaderNodeCustomGroup
from bpy.props import PointerProperty, StringProperty

from toon.shaders import script_abs_path


def create_script_node(node_tree: NodeTree, script_name: str):
    script = node_tree.nodes.new('ShaderNodeScript')
    script.mode = 'EXTERNAL'
    script.filepath = script_abs_path(script_name)

    return script


class ToonNodeBase(ShaderNodeCustomGroup):
    def node_tree_name(self):
        return self.bl_name

    def init_toon_node(self, context: Context, node_tree: NodeTree):
        raise NotImplementedError()

    def init(self, context):
        name = f'.{self.node_tree_name()}'
        node_tree = bpy.data.node_groups.get(name)

        if not node_tree:
            node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')
            self.init_toon_node(context, node_tree)

        # Assignment to `self.node_tree` must always be done last.
        self.node_tree = node_tree

    def free(self):
        if self.node_tree.users == 1:
            bpy.data.node_groups.remove(self.node_tree)


class ToonNodeLightBase(ToonNodeBase):
    last_object_name: StringProperty(default='')  # type: ignore # noqa: F722

    def update_object(self, context: Context):
        self.free()
        self.init(context)

        self.last_object_name = self.object.name if self.object else ''

    object: PointerProperty(
        name='Object',  # noqa: F821
        type=Object,
        update=lambda self, context: self.update_object(context)
    )  # type: ignore

    def node_tree_name(self):
        name = super().node_tree_name()

        return f'{name}_{self.object.name}' if self.object else name

    def draw_buttons(self, context, layout):
        if self.object and self.object.name != self.last_object_name:
            layout.alert = True

        layout.prop(self, 'object', text='Object')
