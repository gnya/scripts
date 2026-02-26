from __future__ import annotations
from typing import Iterator

from bpy.types import NodeTree

from .facade_color import ToonPaletteColor
from .utils import is_palette
from .utils import get_group_name


class ToonPaletteGroup(object):
    def __init__(self, node_tree: NodeTree):
        self.node_tree = node_tree

    @property
    def name(self) -> str:
        return get_group_name(self.node_tree)

    @name.setter
    def name(self, value: str):
        if value == self.name:
            return
        elif value == '':
            value = 'Group'
        else:
            value = value.replace('|', '_')

        names = self.node_tree.name.split('|', 2)
        names[2] = value
        self.node_tree.name = '|'.join(names)

    def add(self, color_name: str) -> bool:
        self.node_tree.outputs.new('NodeSocketColor', color_name)
        index = len(self.node_tree.outputs) - 1
        ToonPaletteColor(index, self.node_tree).init()

        return True

    def remove(self, socket_index: int) -> bool:
        if socket_index < 0 or socket_index >= len(self.node_tree.outputs):
            return False

        socket = self.node_tree.outputs[socket_index]
        self.node_tree.outputs.remove(socket)

        return True

    def colors(self) -> Iterator[ToonPaletteColor]:
        for index in range(len(self.node_tree.outputs)):
            yield ToonPaletteColor(index, self.node_tree)

    def init(self):
        self.node_tree.nodes.new('NodeGroupOutput')

    @staticmethod
    def from_node_tree(node_tree: NodeTree) -> ToonPaletteGroup | None:
        if is_palette(node_tree):
            return ToonPaletteGroup(node_tree)
        else:
            return None
