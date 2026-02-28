from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from .facade_palette import ToonPalette
from .utils import build_node_tree_name, filter_node_trees

if TYPE_CHECKING:
    from bpy.types import BlendDataNodeTrees, NodeTree


class ToonPaletteFacade:
    def __init__(self, node_groups: BlendDataNodeTrees):
        self.node_groups = node_groups

    def add(self, palette_name: str) -> bool:
        if palette_name == "":
            return False

        name = build_node_tree_name(palette_name, "", True, self.node_groups)
        node_tree = self.node_groups.new(name, "ShaderNodeTree")
        node_tree.use_fake_user = True
        node_tree.nodes.new("NodeGroupOutput")

        return True

    def remove(self, palette_name: str) -> bool:
        if palette_name == "":
            return False

        result = False

        name = build_node_tree_name(palette_name, "")

        for node_tree in list(self.node_groups):
            if node_tree.name.startswith(name):
                self.node_groups.remove(node_tree)

                result = True

        return result

    def get(self, palette_name: str) -> ToonPalette | None:
        if palette_name == "":
            return None

        node_trees = list(filter_node_trees(self.node_groups, palette_name))

        if len(node_trees) > 0:
            return ToonPalette(self.node_groups, node_trees[0], node_trees[1:])
        else:
            return None

    def palettes(self) -> Iterator[ToonPalette]:
        palettes: dict[str, tuple[NodeTree, list[NodeTree]]] = {}
        orphan_groups = []

        for node_tree in filter_node_trees(self.node_groups):
            _, palette_name, group_name = node_tree.name.split("|", 2)

            if palette_name not in palettes:
                if group_name == "":
                    palettes[palette_name] = (node_tree, [])
                else:
                    orphan_groups.append(node_tree)
            else:
                palettes[palette_name][1].append(node_tree)

        for palette in palettes.values():
            yield ToonPalette(self.node_groups, *palette)

        if len(orphan_groups) > 0:
            yield ToonPalette(self.node_groups, None, orphan_groups)
