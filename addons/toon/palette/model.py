from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from toon.utils import slice_itr, within

from .naming import (
    build_node_tree_name,
    filter_node_trees,
    is_header,
    resolve_palette_name,
)
from .palette import ToonPalette
from .types import order_to_key

if TYPE_CHECKING:
    from bpy.types import BlendDataNodeTrees, NodeTree


class ToonPaletteFacade:
    def __init__(self, node_groups: BlendDataNodeTrees):
        self.node_groups = node_groups

    def _palettes(self) -> Iterator[ToonPalette]:
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

    def _renumber_order(self):
        for index, palette in enumerate(self.palettes()):
            palette.order = index

    def add(self, palette_name: str) -> bool:
        if palette_name == "":
            return False

        self._renumber_order()

        name = build_node_tree_name(
            resolve_palette_name(self.node_groups, palette_name), ""
        )
        node_tree = self.node_groups.new(name, "ShaderNodeTree")
        node_tree.use_fake_user = True
        node_tree.nodes.new("NodeGroupOutput")

        self._renumber_order()

        return True

    def remove(self, palette_name: str) -> bool:
        if (palette := self.get(palette_name)) is None:
            return False
        else:
            self.node_groups.remove(palette.header)

            for node_tree in palette.node_trees:
                self.node_groups.remove(node_tree)

            return True

    def get(self, palette_name: str) -> ToonPalette | None:
        if palette_name == "":
            return None

        node_trees = list(filter_node_trees(self.node_groups, palette_name))

        if len(node_trees) > 0 and is_header(node_trees[0]):
            return ToonPalette(self.node_groups, node_trees[0], node_trees[1:])
        else:
            return None

    def palettes(self) -> list[ToonPalette]:
        return sorted(self._palettes(), key=lambda p: order_to_key(p.order))

    def move(self, src_index: int, dst_index: int) -> bool:
        palettes = self.palettes()

        if not within(len(palettes), src_index, dst_index):
            return False

        self._renumber_order()
        palettes[src_index].order = dst_index
        offset = 1 if src_index < dst_index else -1

        for index, palette in slice_itr(palettes, src_index, dst_index):
            palette.order = index - offset

        return True
