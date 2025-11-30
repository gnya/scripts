from typing import Any, Iterator, Literal

from bpy.types import bpy_prop_array
from bpy.types import Node, NodeSocket, NodeTree

from toon.utils import node_itr, all_node_users_itr


SocketValue = int | float | list[int | float]
SocketBinder = dict[str, tuple[SocketValue, list[NodeSocket]]]


def _rebind_inputs(node_tree: NodeTree, node: Node, old_id: int, new_id: int):
    old_socket = node.inputs[old_id]
    new_socket = node.inputs[new_id]

    for link in old_socket.links:
        node_tree.links.new(link.from_socket, new_socket)


def _rebind_outputs(node_tree: NodeTree, node: Node, old_id: int, new_id: int):
    old_socket = node.outputs[old_id]
    new_socket = node.outputs[new_id]

    for link in old_socket.links:
        node_tree.links.new(new_socket, link.to_socket)


def change_socket_type(
    node_tree: NodeTree, socket_id: int,
    type: str, in_out: Literal['IN'] | Literal['OUT']
):
    if in_out == 'IN':
        sockets = node_tree.inputs
    else:
        sockets = node_tree.outputs

    old_id = socket_id
    old_interface = sockets[old_id]

    if old_interface.bl_socket_idname == type:
        return

    # Add socket.
    sockets.new(type, old_interface.name)
    new_id = len(sockets) - 1

    if in_out == 'IN':
        inner_node_type = 'NodeGroupInput'
        inner_rebinder = _rebind_outputs
        outer_rebinder = _rebind_inputs
    else:
        inner_node_type = 'NodeGroupOutput'
        inner_rebinder = _rebind_inputs
        outer_rebinder = _rebind_outputs

    # Rebind inner sockets.
    for node in node_itr(node_tree, inner_node_type):
        inner_rebinder(node_tree, node, old_id, new_id)

    # Rebind outer sockets.
    for node in all_node_users_itr(node_tree):
        outer_rebinder(node.id_data, node, old_id, new_id)

    # Move new socket and remove old socket.
    sockets.move(new_id, old_id)
    sockets.remove(old_interface)

    # Update nodes.
    for node in all_node_users_itr(node_tree):
        node.update()


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
