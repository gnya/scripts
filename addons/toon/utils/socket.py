from typing import Any, Iterator

from bpy.types import bpy_prop_array
from bpy.types import Node, NodeSocket, NodeTree


SocketValue = int | float | list[int | float]
SocketBinder = dict[str, tuple[SocketValue, list[NodeSocket]]]


def _bind_sockets(
    node_tree: NodeTree, sockets: Iterator[NodeSocket], binder: SocketBinder
):
    for socket in sockets:
        if socket.enabled:
            value = getattr(socket, 'default_value', None)

            if isinstance(value, bpy_prop_array):
                value = list(value)
            elif not isinstance(value, (int, float)):
                value = None

            if socket.is_output:
                binded_sockets = [l.to_socket for l in socket.links]
            else:
                binded_sockets = [l.from_socket for l in socket.links]

            binder[socket.name] = (value, binded_sockets)

    # Remove all links.
    for socket in sockets:
        for link in socket.links:
            node_tree.links.remove(link)


def _rebind_sockets(
    node_tree: NodeTree, sockets: Iterator[NodeSocket], binder: SocketBinder
):
    for socket in sockets:
        if socket.enabled and socket.name in binder:
            value, binded_sockets = binder[socket.name]

            try:
                setattr(socket, 'default_value', value)
            except TypeError:
                pass
            except AttributeError:
                pass

            if socket.is_output:
                for s in binded_sockets:
                    node_tree.links.new(socket, s)
            else:
                for s in binded_sockets:
                    node_tree.links.new(s, socket)


class NodeLinkRebinder():
    def __init__(self, node: Node):
        self.node = node
        self.inputs: SocketBinder = {}
        self.outputs: SocketBinder = {}

    def __enter__(self):
        node_tree = self.node.id_data
        _bind_sockets(node_tree, self.node.inputs, self.inputs)
        _bind_sockets(node_tree, self.node.outputs, self.outputs)

        return self

    def __exit__(self, *exc: Any):
        node_tree = self.node.id_data
        _rebind_sockets(node_tree, self.node.inputs, self.inputs)
        _rebind_sockets(node_tree, self.node.outputs, self.outputs)
