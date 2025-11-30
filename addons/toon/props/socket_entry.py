from __future__ import annotations
from typing import Iterator
from toon.utils import override

from bpy.types import NodeSocket, NodeSocketInterface, NodeTree
from bpy.props import IntProperty

from toon.utils import change_socket_type

from .base import Entry, EntryBase


class SocketEntry(Entry):
    socket_id: IntProperty(default=-1)

    def _next_of_self(self):
        find_self = False

        for entry in self.linked_entries():
            if entry == self:
                find_self = True
            elif find_self:
                return entry

        return None

    def node_tree(self) -> NodeTree:
        raise NotImplementedError()

    def linked_entries(self) -> Iterator[SocketEntry]:
        raise NotImplementedError()

    def socket_interface(self) -> NodeSocketInterface:
        return self.node_tree().outputs[self.socket_id]

    def socket(self) -> NodeSocket:
        node_tree = self.node_tree()
        output = node_tree.nodes.get('Group Output')

        if output is None:
            output = node_tree.nodes.new('NodeGroupOutput')

        return output.inputs[self.socket_id]

    def change_socket_type(self, type: str):
        change_socket_type(
            self.node_tree(), self.socket_id, type, 'OUT'
        )

    @override
    def compare(self, other: EntryBase) -> int:
        other_socket_id = getattr(other, 'socket_id', -1)

        return self.socket_id - other_socket_id

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
        if (dst_entry := self._next_of_self()) is not None:
            self.on_move(dst_entry)

    @override
    def on_remove(self):
        # Remove socket.
        socket_id = self.socket_id
        node_tree = self.node_tree()
        socket = node_tree.outputs[socket_id]
        node_tree.outputs.remove(socket)

        # Adjust the socket_id for consistency.
        for entry in self.linked_entries():
            if entry.socket_id > socket_id:
                entry.socket_id -= 1

    @override
    def on_move(self, dst: EntryBase):
        src_id = self.socket_id
        dst_id = getattr(dst, 'socket_id', -1)

        if dst_id < 0 or src_id == dst_id:
            return

        # Move socket.
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

        for entry in self.linked_entries():
            socket_id = entry.socket_id

            if socket_id > min_id and socket_id < max_id:
                entry.socket_id += offset

        self.socket_id = dst_id
