from toon.utils import override

from bpy.props import (
    EnumProperty, FloatProperty, FloatVectorProperty,
    IntVectorProperty, StringProperty
)
from bpy.types import (
    Context, Image, Node, NodeSocket, NodeTree, PropertyGroup
)

from toon.utils import from_node

from .socket_entry import SocketEntry


class PaletteEntry(SocketEntry, PropertyGroup):
    entry_types = [
        ('COLOR', 'Color', '', 'COLOR', 0),
        ('TEXTURE', 'Texture', '', 'IMAGE_DATA', 1),
        ('VALUE', 'Value', '', 'PROPERTIES', 2),
        ('MIX', 'Mix', '', 'DOT', 3)
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

    def _update_texture_uv_snap_size(self, context: Context):
        snap = self.node('CUSTOM GROUP')

        if snap is not None:
            snap.inputs[1].default_value = self.texture_uv_snap_size[0]
            snap.inputs[2].default_value = self.texture_uv_snap_size[1]

    def _update_texture_uv_map(self, context: Context):
        uv = self.node('UVMAP')

        if uv is not None:
            uv.uv_map = self.texture_uv_map

    def _update_value(self, context: Context):
        value = self.node()

        if value is not None:
            value.outputs[0].default_value = self.value

    def _update_mix_factor(self, context: Context):
        mix = self.node()

        if mix is not None:
            mix.inputs[0].default_value = self.mix_factor

    def _update_mix_source(self, context: Context):
        self._remove_branch(self._root())
        self._init_branch()

    type: EnumProperty(
        name='Type', description='Type of entry',
        items=entry_types, default='COLOR',
        update=_update_type
    )

    color: FloatVectorProperty(
        name='Color', subtype='COLOR', size=4, soft_min=0.0, soft_max=1.0,
        update=_update_color
    )

    texture_uv_snap_size: IntVectorProperty(
        name='UV Snap Size', size=2,
        update=_update_texture_uv_snap_size
    )

    texture_uv_map: StringProperty(
        name='UV Map',
        update=_update_texture_uv_map
    )

    value: FloatProperty(
        name='Value', default=0, soft_min=0.0, soft_max=1.0,
        update=_update_value
    )

    mix_factor: FloatProperty(
        name='Factor', default=0, soft_min=0.0, soft_max=1.0,
        update=_update_mix_factor
    )

    mix_source_a: StringProperty(
        name='Source A',
        update=_update_mix_source
    )

    mix_source_b: StringProperty(
        name='Source B',
        update=_update_mix_source
    )

    @property
    def texture_image(self) -> Image | None:
        if self.type == 'TEXTURE':
            node = self.node()

            if node is not None:
                return node.image

        return None

    @texture_image.setter
    def texture_image(self, value: Image):
        if self.type == 'TEXTURE':
            node = self.node()

            if node is not None:
                node.image = value
                self.texture_uv_snap_size = value.size

    def _root(self) -> NodeSocket:
        return self.socket().links[0].from_node.inputs[0]

    def _init_root(self):
        node_tree = self.node_tree()
        reroute = node_tree.nodes.new('NodeReroute')
        node_tree.links.new(reroute.outputs[0], self.socket())

    def _init_branch(self):
        node_tree = self.node_tree()

        if self.type == 'COLOR':
            self.change_socket_type('NodeSocketColor')

            rgb = node_tree.nodes.new('ShaderNodeRGB')
            rgb.outputs[0].default_value = self.color
            node_tree.links.new(rgb.outputs[0], self._root())
        elif self.type == 'TEXTURE':
            self.change_socket_type('NodeSocketColor')

            tex = node_tree.nodes.new('ShaderNodeTexImage')
            tex.interpolation = 'Closest'
            node_tree.links.new(tex.outputs[0], self._root())

            snap = node_tree.nodes.new('ToonNodeUVPixelSnap')
            node_tree.links.new(snap.outputs[0], tex.inputs[0])

            uv = node_tree.nodes.new('ShaderNodeUVMap')
            node_tree.links.new(uv.outputs[0], snap.inputs[0])
        elif self.type == 'VALUE':
            self.change_socket_type('NodeSocketFloat')

            value = node_tree.nodes.new('ShaderNodeValue')
            value.outputs[0].default_value = self.value
            node_tree.links.new(value.outputs[0], self._root())
        elif self.type == 'MIX':
            self.change_socket_type('NodeSocketColor')

            mix = node_tree.nodes.new('ShaderNodeMixRGB')
            mix.inputs[0].default_value = self.mix_factor
            node_tree.links.new(mix.outputs[0], self._root())
            parent = self.parent()

            if parent is None:
                return

            a = parent.first(self.mix_source_a)
            b = parent.first(self.mix_source_b)

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

    def node(self, type: str = '') -> Node | None:
        root = self._root()

        if root is None or len(root.links) == 0:
            return None

        if not type:
            return from_node(root)
        else:
            return from_node(root, {type})
