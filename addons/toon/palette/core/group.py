from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from toon.utils import within

from .color import ToonPaletteColor
from .naming import get_group_name, get_group_name_full, get_library, resolve_group_name
from .types import get_order, set_order

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

        names = self.node_tree.name.split("|", 2)
        names[2] = resolve_group_name(value)
        self.node_tree.name = "|".join(names)

    @property
    def name_full(self) -> str:
        return get_group_name_full(self.node_tree)

    @property
    def library(self) -> str:
        return get_library(self.node_tree)

    @property
    def order(self) -> int:
        return get_order(self.node_tree)

    @property
    def is_linked(self) -> bool:
        return self.library != ""

    @order.setter
    def order(self, value: int):
        set_order(self.node_tree, value)

    def add(self, color_name: str) -> ToonPaletteColor:
        if self.is_linked:
            raise RuntimeError("Linked palette is read-only.")

        self.node_tree.outputs.new("NodeSocketColor", color_name)
        color = ToonPaletteColor(self.node_tree, self.size() - 1)
        color.init()

        return color

    def remove(self, index: int) -> bool:
        if not within(self.size(), index):
            return False
        elif self.is_linked:
            raise RuntimeError("Linked palette is read-only.")

        socket = self.node_tree.outputs[index]
        self.node_tree.outputs.remove(socket)

        return True

    def colors(self) -> Iterator[ToonPaletteColor]:
        for index in range(self.size()):
            yield ToonPaletteColor(self.node_tree, index)

    def size(self) -> int:
        return len(self.node_tree.outputs)

    def move(self, src_index: int, dst_index: int) -> bool:
        if not within(self.size(), src_index, dst_index):
            return False
        elif self.is_linked:
            raise RuntimeError("Linked palette is read-only.")

        self.node_tree.outputs.move(src_index, dst_index)

        return True

    def init(self):
        self.node_tree.use_fake_user = True
        self.node_tree.nodes.new("NodeGroupOutput")
