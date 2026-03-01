from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from toon.utils import slice_itr, within

from .group import ToonPaletteGroup
from .naming import (
    build_node_tree_name,
    get_palette_name,
    resolve_group_name,
    resolve_palette_name,
)
from .types import get_order, order_to_key, set_order

if TYPE_CHECKING:
    from bpy.types import BlendDataNodeTrees, NodeTree


class ToonPalette:
    def __init__(
        self,
        node_groups: BlendDataNodeTrees,
        header: NodeTree | None,
        node_trees: list[NodeTree],
    ):
        self.node_groups = node_groups
        self.header = header
        self.node_trees = node_trees

    def _groups(self) -> Iterator[ToonPaletteGroup]:
        for node_tree in self.node_trees:
            yield ToonPaletteGroup(node_tree)

    def _renumber_order(self):
        for index, group in enumerate(self.groups()):
            group.order = index

    @property
    def name(self) -> str:
        return get_palette_name(self.header)

    @name.setter
    def name(self, value: str):
        if self.header is None or value == self.name:
            return

        name = build_node_tree_name(self.name, "")
        new_name = build_node_tree_name(
            resolve_palette_name(self.node_groups, value), ""
        )

        self.header.name = self.header.name.replace(name, new_name, 1)

        for node_tree in self.node_trees:
            node_tree.name = node_tree.name.replace(name, new_name, 1)

    @property
    def order(self) -> int:
        return get_order(self.header)

    @order.setter
    def order(self, value: int):
        set_order(self.header, value)

    def add(self, group_name: str) -> ToonPaletteGroup:
        if self.header is None:
            raise RuntimeError("No header found in this palette.")

        self._renumber_order()

        name = build_node_tree_name(self.name, resolve_group_name(group_name))
        node_tree = self.node_groups.new(name, "ShaderNodeTree")
        group = ToonPaletteGroup(node_tree)
        group.init()

        self.node_trees.append(node_tree)
        self._renumber_order()

        return group

    def remove(self, group_name: str) -> bool:
        if (group := self.get(group_name)) is None:
            return False
        else:
            self.node_groups.remove(group.node_tree)

            return True

    def get(self, group_name: str) -> ToonPaletteGroup | None:
        for group in self._groups():
            if group.name == group_name:
                return group

        return None

    def groups(self) -> list[ToonPaletteGroup]:
        return sorted(self._groups(), key=lambda g: order_to_key(g.order))

    def size(self) -> int:
        return len(self.node_trees)

    def dist(self, index_a: int, index_b: int) -> int:
        groups = self.groups()

        if not within(self.size(), index_a, index_b):
            return -1

        return sum(g.size() + 1 for _, g in slice_itr(groups, index_a, index_b))

    def move(self, src_index: int, dst_index: int) -> bool:
        groups = self.groups()

        if not within(self.size(), src_index, dst_index):
            return False

        self._renumber_order()
        groups[src_index].order = dst_index
        offset = 1 if src_index < dst_index else -1

        for index, group in slice_itr(groups, src_index, dst_index):
            group.order = index - offset

        return True

    def init(self):
        if self.header is not None:
            self.header.use_fake_user = True
