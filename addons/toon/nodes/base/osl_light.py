from toon.utils import override

import bpy
import re

from bpy.types import Context, Node, NodeTree, Object, UILayout
from bpy.props import PointerProperty, StringProperty

from toon.utils import subscribe_rna, NodeLinkRebinder

from .osl import ToonNodeOSL


class ToonNodeOSLLight(ToonNodeOSL):
    def _poll_object(self, object: Object):
        return object.type in {'LIGHT', 'EMPTY'}

    def _update_object(self, context: Context):
        with NodeLinkRebinder(self):
            self.free()
            self.init(context)

        if self.object is None:
            self.last_object_name = ''
        else:
            self.last_object_name = self.object.name

    last_object_name: StringProperty(default='')

    object: PointerProperty(
        name='Object', type=Object,
        poll=_poll_object, update=_update_object
    )

    def new_attr_node(self, node_tree: NodeTree, attr: str) -> Node:
        if self.object is None:
            attribute_name = ''
        else:
            attribute_name = f'objects["{self.object.name}"].{attr}'

        node = node_tree.nodes.new('ShaderNodeAttribute')
        node.name = 'Attribute Rotation'
        node.attribute_type = 'VIEW_LAYER'
        node.attribute_name = attribute_name

        return node

    @override
    def node_tree_key(self) -> tuple[str, str]:
        name, lib = super().node_tree_key()

        return f'{name}_{self.object.name}' if self.object else name, lib

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
        layout.prop(self, 'object', text='Object')

    def _update_attr_node(self, node: Node):
        attr = node.attribute_name

        if m := re.match(r'^(objects\[").*("\].*)$', attr):
            attr = f'{m.group(1)}{self.object.name}{m.group(2)}'
            node.attribute_name = attr

    def _update_attr_nodes(self) -> bool:
        if self.object is None:
            return False
        elif self.object.name == self.last_object_name:
            return False

        node_tree = self.node_tree

        if node_tree is None:
            return False

        for node in node_tree.nodes:
            if node.type == 'ATTRIBUTE':
                self._update_attr_node(node)

        self.last_object_name = self.object.name

        # To avoid name conflicts during renaming,
        # a temporary placeholder name is assigned first.
        node_tree.name = f'.TEMP_{self.bl_idname}'

        return True

    @staticmethod
    def _update_all_attr_nodes():
        nodes: list[ToonNodeOSLLight] = []

        for material in bpy.data.materials:
            if material.node_tree is not None:
                for node in material.node_tree.nodes:
                    if not isinstance(node, ToonNodeOSLLight):
                        continue
                    elif node._update_attr_nodes():
                        nodes.append(node)

        for node_tree in bpy.data.node_groups:
            if not node_tree.name.startswith('.'):
                for node in node_tree.nodes:
                    if not isinstance(node, ToonNodeOSLLight):
                        continue
                    elif node._update_attr_nodes():
                        nodes.append(node)

        for node in nodes:
            if node.node_tree is None:
                continue

            node.node_tree.name, _ = node.node_tree_key()

    @staticmethod
    def register():
        subscribe_rna(
            (Object, 'name'),
            ToonNodeOSLLight._update_all_attr_nodes
        )
