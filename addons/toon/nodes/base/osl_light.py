from toon.utils import override

import bpy
import re

from bpy.types import Context, Node, NodeTree, Object, UILayout
from bpy.props import PointerProperty, StringProperty

from toon.utils import object_rename_post, NodeLinkRebinder

from .osl import ToonNodeOSL


class ToonNodeOSLLight(ToonNodeOSL):
    def _poll_object(self, object: Object) -> bool:
        if object.library is not None:
            return False

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

    def _attr_prefix(self):
        if self.object is None:
            return ''

        return f'objects["{self.object.name}"]'

    def _get_node_tree(self, name: str) -> NodeTree | None:
        prefix = self._attr_prefix()

        for node_tree in bpy.data.node_groups:
            if not node_tree.name.startswith(name):
                continue

            for node in node_tree.nodes:
                if node.type != 'ATTRIBUTE':
                    continue

                attr = node.attribute_name

                if not prefix:
                    if not attr:
                        return node_tree
                    else:
                        continue
                elif attr.startswith(prefix):
                    return node_tree

        return None

    def _update_attr_nodes(self, obj: Object):
        if not obj or obj != self.object:
            return
        elif obj.name == self.last_object_name:
            return

        node_tree = self.node_tree

        if node_tree is None:
            return

        for node in node_tree.nodes:
            if node.type != 'ATTRIBUTE':
                continue

            prefix = self._attr_prefix()
            attr_old = node.attribute_name
            attr_new = re.sub(r'^objects\[".*"\]', prefix, attr_old)
            node.attribute_name = attr_new

        self.last_object_name = obj.name

    @staticmethod
    def _update_all_attr_nodes(obj: Object, last_name: str):
        for material in bpy.data.materials:
            if material.node_tree is None:
                continue

            for node in material.node_tree.nodes:
                if not isinstance(node, ToonNodeOSLLight):
                    continue

                node._update_attr_nodes(obj)

        for node_tree in bpy.data.node_groups:
            if node_tree.name[0] == '.':
                continue

            for node in node_tree.nodes:
                if not isinstance(node, ToonNodeOSLLight):
                    continue

                node._update_attr_nodes(obj)

    def new_attr_node(self, node_tree: NodeTree, attr: str) -> Node:
        prefix = self._attr_prefix()
        attribute_name = f'{prefix}.{attr}' if prefix else ''

        node = node_tree.nodes.new('ShaderNodeAttribute')
        node.name = 'Attribute Rotation'
        node.attribute_type = 'VIEW_LAYER'
        node.attribute_name = attribute_name

        return node

    @override
    def get_node_tree(self) -> NodeTree | None:
        name, _ = self.node_tree_key()

        if not name:
            return None

        node_tree = self._get_node_tree(name)

        if node_tree is None:
            return self.new_node_tree(name)
        else:
            return node_tree

    @override
    def draw_buttons(self, context: Context, layout: UILayout):
        layout.prop(self, 'object', text='Object')

    @classmethod
    def register(cls):
        if cls._update_all_attr_nodes not in object_rename_post:
            object_rename_post.append(cls._update_all_attr_nodes)
