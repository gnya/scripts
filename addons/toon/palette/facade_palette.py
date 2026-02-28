from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from .facade_group import ToonPaletteGroup
from .utils import build_node_tree_name, get_palette_name

if TYPE_CHECKING:
    from bpy.types import BlendDataNodeTrees, NodeTree


class ToonPalette:
    def __init__(
        self,
        node_groups: BlendDataNodeTrees,
        header: NodeTree,
        node_trees: list[NodeTree],
    ):
        self.node_groups = node_groups
        self.header = header
        self.node_trees = node_trees

    @property
    def name(self) -> str:
        return get_palette_name(self.header)

    @name.setter
    def name(self, value: str):
        if value == self.name:
            return
        elif value == "":
            value = "Palette"
        else:
            value = value.replace("|", "_")

        name = build_node_tree_name(self.name, "")
        new_name = build_node_tree_name(value, "", True, self.node_groups)

        self.header.name = self.header.name.replace(name, new_name, 1)

        for node_tree in self.node_trees:
            node_tree.name = node_tree.name.replace(name, new_name, 1)

    def add(self, group_name: str) -> bool:
        if group_name == "":
            return False

        name = build_node_tree_name(self.name, group_name)
        node_tree = self.node_groups.new(name, "ShaderNodeTree")
        node_tree.use_fake_user = True
        ToonPaletteGroup(node_tree).init()

        self.node_trees.append(node_tree)

        return True

    def remove(self, group_name: str) -> bool:
        if group_name == "":
            return False

        name = build_node_tree_name(self.name, group_name)

        for node_tree in self.node_trees:
            if node_tree.name == name:
                self.node_groups.remove(node_tree)

                return True

        return False

    def get(self, group_name: str) -> ToonPaletteGroup | None:
        for node_tree in self.node_trees:
            if node_tree.name.split("|", 2)[2] == group_name:
                return ToonPaletteGroup(node_tree)

        return None

    def groups(self) -> Iterator[ToonPaletteGroup]:
        for node_tree in self.node_trees:
            yield ToonPaletteGroup(node_tree)
