from bpy.types import NodeSocket, NodeSocketInterface, NodeTree
from bpy.props import IntProperty
from typing import Iterator

from .base import DataItem


class SocketLinkedItem(DataItem):
    socket_id: IntProperty(default=-1)

    @property
    def node_tree(self) -> NodeTree:
        raise NotImplementedError()

    @property
    def socket_interface(self) -> NodeSocketInterface:
        return self.node_tree.outputs[self.socket_id]

    @property
    def socket(self) -> NodeSocket:
        output = self.node_tree.nodes.get('Group Output')

        if not output:
            output = self.node_tree.nodes.new('NodeGroupOutput')

        return output.inputs[self.socket_id]

    def linked_items(self) -> Iterator['SocketLinkedItem']:
        raise NotImplementedError()

    def _next_of_self(self):
        find_self = False

        for item in self.linked_items():
            if item == self:
                find_self = True
            elif find_self:
                return item

        return None

    def compare(self, other):
        return self.socket_id - other.socket_id

    def on_rename(self):
        self.socket_interface.name = self.name

    def on_add(self):
        # Add socket.
        self.node_tree.outputs.new('NodeSocketColor', '')
        self.socket_id = len(self.node_tree.outputs) - 1

        # Reposition the socket from the end to the proper location.
        if (dst_item := self._next_of_self()) is not None:
            self.on_move(dst_item)

    def on_remove(self):
        # Remove socket.
        socket_id = self.socket_id
        socket = self.node_tree.outputs[socket_id]
        self.node_tree.outputs.remove(socket)

        # Adjust the socket_id for consistency.
        for item in self.linked_items():
            if item.socket_id > socket_id:
                item.socket_id -= 1

    def on_move(self, dst):
        # Move socket.
        src_socket_id = self.socket_id
        dst_socket_id = dst.socket_id
        self.node_tree.outputs.move(src_socket_id, dst_socket_id)

        # Adjust the socket_id for consistency.
        min_socket_id = src_socket_id
        max_socket_id = dst_socket_id + 1
        offset = -1

        if src_socket_id > dst_socket_id:
            min_socket_id = dst_socket_id - 1
            max_socket_id = src_socket_id
            offset = 1

        for item in self.linked_items():
            socket_id = item.socket_id

            if socket_id > min_socket_id and socket_id < max_socket_id:
                item.socket_id += offset

        self.socket_id = dst_socket_id
