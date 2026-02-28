from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from .color import ToonPaletteColor
from .utils import get_group_name

if TYPE_CHECKING:
    from bpy.types import NodeTree


class ToonPaletteGroup:
    def __init__(self, node_tree: NodeTree):
        self.node_tree = node_tree

    @property
    def name(self) -> str:
        return get_group_name(self.node_tree)

    @name.setter
    def name(self, value: str):
        if value == self.name:
            return
        elif value == "":
            value = "Group"
        else:
            value = value.replace("|", "_")

        names = self.node_tree.name.split("|", 2)
        names[2] = value
        self.node_tree.name = "|".join(names)

    def add(self, color_name: str) -> bool:
        self.node_tree.outputs.new("NodeSocketColor", color_name)
        index = len(self.node_tree.outputs) - 1
        ToonPaletteColor(self.node_tree, index).init()

        return True

    def remove(self, index: int) -> bool:
        if index < 0 or index >= len(self.node_tree.outputs):
            return False

        socket = self.node_tree.outputs[index]
        self.node_tree.outputs.remove(socket)

        return True

    def colors(self) -> Iterator[ToonPaletteColor]:
        for index in range(len(self.node_tree.outputs)):
            yield ToonPaletteColor(self.node_tree, index)

    def move(self, src_index: int, dst_index: int) -> bool:
        if src_index < 0 or src_index >= len(self.node_tree.outputs):
            return False

        if dst_index < 0 or dst_index >= len(self.node_tree.outputs):
            return False

        self.node_tree.outputs.move(src_index, dst_index)

        return True

    def init(self):
        self.node_tree.nodes.new("NodeGroupOutput")
