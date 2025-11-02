import bpy
import os


def create_script_node(node_tree, osl_name):
    addon_path = os.path.dirname(os.path.abspath(__file__))
    script = node_tree.nodes.new('ShaderNodeScript')
    script.mode = 'EXTERNAL'
    script.filepath = f'{addon_path}\\shader\\{osl_name}.osl'

    return script


class ToonNodeBase(bpy.types.ShaderNodeCustomGroup):
    def init_toon_node(self, context, node_tree):
        raise NotImplementedError()

    def init(self, context):
        name = f'.{self.bl_name}'
        node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')
        self.init_toon_node(context, node_tree)

        # Assignment to `self.node_tree` must always be done last.
        self.node_tree = node_tree

    def copy(self, node):
        self.node_tree = node.node_tree.copy()

    def free(self):
        bpy.data.node_groups.remove(self.node_tree)


class ToonNodeLightBase(ToonNodeBase):
    def update_object(self, context):
        raise NotImplementedError()

    object: bpy.props.PointerProperty(
        type=bpy.types.Object,
        update=lambda self, context: self.update_object(context)
    )  # type: ignore

    def draw_buttons(self, context, layout):
        layout.prop(self, 'object', text='Object')
