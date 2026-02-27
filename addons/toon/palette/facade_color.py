from typing import Any

from bpy.types import NodeSocket, NodeSocketInterface, NodeTree

from toon.utils import remove_nodes
from toon.utils import search_node
from toon.utils import change_socket_type

from .utils import ToonPaletteColorTypes


class ToonPaletteColor:
    def __init__(self, index: int, node_tree: NodeTree) -> None:
        self.socket_index = index
        self.node_tree = node_tree

    @property
    def name(self) -> str:
        return self.node_tree.outputs[self.socket_index].name

    @name.setter
    def name(self, value: str):
        self.node_tree.outputs[self.socket_index].name = value

    def _socket(self) -> NodeSocket:
        output = self.node_tree.nodes.get('Group Output')

        if output is None:
            raise RuntimeError('NodeGroupOutput is missing.')

        return output.inputs[self.socket_index]

    def _socket_interface(self) -> NodeSocketInterface:
        return self.node_tree.outputs[self.socket_index]

    @property
    def type(self) -> ToonPaletteColorTypes:
        socket = self._socket()

        if len(socket.links) == 0:
            type = self._socket_interface().bl_socket_idname

            if type == 'NodeSocketColor':
                return 'COLOR'
            elif type == 'NodeSocketVector':
                return 'VECTOR'
            elif type == 'NodeSocketFloat':
                return 'VALUE'

        if search_node(socket, 'ShaderNodeTexImage') is not None:
            return 'TEXTURE'
        else:
            raise ValueError(f'Unknown socket type. : {socket}')

    @type.setter
    def type(self, value: ToonPaletteColorTypes):
        remove_nodes(self._socket())

        if value == 'COLOR':
            change_socket_type(
                self.node_tree, self.socket_index, 'NodeSocketColor', 'OUT'
            )

            self._socket().default_value = (1.0, 1.0, 1.0, 1.0)
        elif value == 'TEXTURE':
            change_socket_type(
                self.node_tree, self.socket_index, 'NodeSocketColor', 'OUT'
            )

            uv = self.node_tree.nodes.new('ShaderNodeUVMap')
            snap = self.node_tree.nodes.new('ToonNodeUVPixelSnap')
            self.node_tree.links.new(uv.outputs[0], snap.inputs[0])

            tex = self.node_tree.nodes.new('ShaderNodeTexImage')
            tex.interpolation = 'Closest'
            self.node_tree.links.new(snap.outputs[0], tex.inputs[0])
            self.node_tree.links.new(tex.outputs[0], self._socket())
        elif value == 'VECTOR':
            change_socket_type(
                self.node_tree, self.socket_index, 'NodeSocketVector', 'OUT'
            )

            self._socket().default_value = (0.0, 0.0, 0.0)
            self._socket_interface().min_value = -1.0
            self._socket_interface().max_value = 1.0
        elif value == 'VALUE':
            change_socket_type(
                self.node_tree, self.socket_index, 'NodeSocketFloat', 'OUT'
            )

            self._socket().default_value = 0.0
            self._socket_interface().min_value = 0.0
            self._socket_interface().max_value = 1.0
        else:
            raise ValueError(f'Unknown color type. : {value}')

    @property
    def color_ptr(self) -> tuple[Any, str]:
        return self._socket(), 'default_value'

    @property
    def texture_ptr(self) -> tuple[Any, str]:
        node = search_node(self._socket(), 'ShaderNodeTexImage')

        if node is None:
            return None, ''

        return node, 'image'

    @property
    def uv_pixel_snap_ptr(self) -> tuple[tuple[Any, str], tuple[Any, str]]:
        node = search_node(self._socket(), 'ToonNodeUVPixelSnap')

        if node is None:
            return (None, ''), (None, '')

        inputs = node.inputs

        return (inputs[1], 'default_value'), (inputs[2], 'default_value')

    @property
    def uv_map_ptr(self) -> tuple[Any, str]:
        node = search_node(self._socket(), 'ShaderNodeUVMap')

        if node is None:
            return '', ''

        return node, 'uv_map'

    def init(self):
        self.type = 'COLOR'
