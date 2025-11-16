from toon.utils import override

from bpy.props import (
    EnumProperty, FloatProperty,
    FloatVectorProperty, StringProperty
)
from bpy.types import Context, Node, NodeSocket, NodeTree, PropertyGroup

from .socket_entry import SocketEntry


class PaletteEntry(SocketEntry, PropertyGroup):
    entry_types = [
        ('COLOR', 'Color', '', 'COLOR', 0),
        ('TEXTURE', 'Texture', '', 'TEXTURE', 1),
        ('MIX', 'Mix', '', 'PROPERTIES', 2)
    ]

    def _update_type(self, context: Context):
        self._remove_branch(self._root())

        if self.type == 'MIX':
            self._remove_branch(self.socket(), forced=True)
            self._init_root()

        self._init_branch()

    def _update_color(self, context: Context):
        rgb = self.node()

        if rgb is not None:
            rgb.outputs[0].default_value = self.color

    def _update_mix_factor(self, context: Context):
        mix = self.node()

        if mix is not None:
            mix.inputs[0].default_value = self.mix_factor

    def _update_mix_source(self, context: Context):
        self._remove_branch(self._root())
        self._init_branch()

    type: EnumProperty(
        items=entry_types, default='COLOR',
        update=_update_type
    )

    color: FloatVectorProperty(
        subtype='COLOR', size=4, soft_min=0.0, soft_max=1.0,
        update=_update_color
    )

    mix_factor: FloatProperty(
        default=0, soft_min=0.0, soft_max=1.0,
        update=_update_mix_factor
    )

    mix_source_a: StringProperty(update=_update_mix_source)

    mix_source_b: StringProperty(update=_update_mix_source)

    def _root(self) -> NodeSocket:
        return self.socket().links[0].from_node.inputs[0]

    def _init_root(self):
        node_tree = self.node_tree()
        reroute = node_tree.nodes.new('NodeReroute')
        node_tree.links.new(reroute.outputs[0], self.socket())

    def _init_branch(self):
        node_tree = self.node_tree()

        if self.type == 'COLOR':
            rgb = node_tree.nodes.new('ShaderNodeRGB')
            rgb.outputs[0].default_value = self.color
            node_tree.links.new(rgb.outputs[0], self._root())
        elif self.type == 'TEXTURE':
            tex = node_tree.nodes.new('ShaderNodeTexImage')
            tex.interpolation = 'Closest'
            node_tree.links.new(tex.outputs[0], self._root())
        elif self.type == 'MIX':
            mix = node_tree.nodes.new('ShaderNodeMixRGB')
            mix.inputs[0].default_value = self.mix_factor
            node_tree.links.new(mix.outputs[0], self._root())
            parent = self.parent()

            if parent is not None:
                a = parent.get_entry(self.mix_source_a)
                b = parent.get_entry(self.mix_source_b)

                if a is not None and a.type != 'MIX':
                    output = a.socket().links[0].from_socket
                    node_tree.links.new(output, mix.inputs[1])

                if b is not None and b.type != 'MIX':
                    output = b.socket().links[0].from_socket
                    node_tree.links.new(output, mix.inputs[2])

    def _remove_branch(self, root: NodeSocket, forced: bool = False):
        if len(root.links) == 0:
            return

        link = root.links[0]
        output = link.from_socket

        if not forced and len(output.links) > 1:
            return

        node = link.from_node

        for input in node.inputs:
            self._remove_branch(input)

        self.node_tree().nodes.remove(node)

    @override
    def node_tree(self) -> NodeTree:
        return self.id_data

    @override
    def linked_entries(self):
        path = self.path_from_id().rsplit('.', 2)[0]
        palette = self.id_data.path_resolve(path)

        for group in palette.entries:
            for entry in group.entries:
                yield entry

    def node(self) -> Node | None:
        root = self._root()

        if root is None or len(root.links) == 0:
            return None

        return root.links[0].from_node

    @override
    def on_add(self):
        super().on_add()

        self._init_root()
        self._init_branch()

    @override
    def on_remove(self):
        if self.type == 'MIX':
            self._remove_branch(self.socket())
        else:
            self._remove_branch(self.socket(), forced=True)

        super().on_remove()
