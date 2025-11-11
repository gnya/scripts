from bpy.types import NodeSocket, NodeSocketInterface, NodeTree
from bpy.props import IntProperty
from typing import Iterator

from toon.utils import override
from toon.utils.collection import Entry


class SocketEntry(Entry):
    socket_id: IntProperty(default=-1)

    def _next_of_self(self):
        find_self = False

        for item in self.linked_items():
            if item == self:
                find_self = True
            elif find_self:
                return item

        return None

    def node_tree(self) -> NodeTree:
        raise NotImplementedError()

    def linked_items(self) -> Iterator['SocketEntry']:
        raise NotImplementedError()

    def socket_interface(self) -> NodeSocketInterface:
        return self.node_tree().outputs[self.socket_id]

    def socket(self) -> NodeSocket:
        node_tree = self.node_tree()
        output = node_tree.nodes.get('Group Output')

        if not output:
            output = node_tree.nodes.new('NodeGroupOutput')

        return output.inputs[self.socket_id]

    @override
    def compare(self, other):
        return self.socket_id - other.socket_id

    @override
    def on_rename(self):
        self.socket_interface().name = self.name

    @override
    def on_add(self):
        # Add socket.
        node_tree = self.node_tree()
        node_tree.outputs.new('NodeSocketColor', '')
        self.socket_id = len(node_tree.outputs) - 1

        # Reposition the socket from the end to the proper location.
        if (dst_item := self._next_of_self()) is not None:
            self.on_move(dst_item)

    @override
    def on_remove(self):
        # Remove socket.
        socket_id = self.socket_id
        node_tree = self.node_tree()
        socket = node_tree.outputs[socket_id]
        node_tree.outputs.remove(socket)

        # Adjust the socket_id for consistency.
        for item in self.linked_items():
            if item.socket_id > socket_id:
                item.socket_id -= 1

    @override
    def on_move(self, dst):
        # Move socket.
        src_id = self.socket_id
        dst_id = dst.socket_id
        node_tree = self.node_tree()
        node_tree.outputs.move(src_id, dst_id)

        # Adjust the socket_id for consistency.
        min_id = src_id
        max_id = dst_id + 1
        offset = -1

        if src_id > dst_id:
            min_id = dst_id - 1
            max_id = src_id
            offset = 1

        for item in self.linked_items():
            socket_id = item.socket_id

            if socket_id > min_id and socket_id < max_id:
                item.socket_id += offset

        self.socket_id = dst_id
