from toon.utils import override

import bpy

from bpy.types import (
    Context, Node, NodeTree, Object, ShaderNodeCustomGroup, UILayout
)
from bpy.props import PointerProperty, StringProperty

from toon.shaders import script_filepath
from toon.utils import NodeLinkRebinder


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

        if node_tree is not None and node_tree.users == 1:
            bpy.data.node_groups.remove(node_tree)


class ToonNodeOSL(ToonNodeGroup):
    osl_name = ''

    def init_node_tree(self, node_tree: NodeTree, script: Node):
        pass

    @override
    def new_node_tree(self, name: str) -> NodeTree:
        node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')
        script = node_tree.nodes.new('ShaderNodeScript')
        script.mode = 'EXTERNAL'
        script.filepath = script_filepath(self.osl_name)
        self.init_node_tree(node_tree, script)

        return node_tree


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
