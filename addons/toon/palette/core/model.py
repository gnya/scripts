from __future__ import annotations

from typing import TYPE_CHECKING

from toon.utils import slice_itr, within

from .naming import build_node_tree_name, filter_node_trees, resolve_palette_name
from .palette import ToonPalette
from .types import order_to_key

if TYPE_CHECKING:
    from bpy.types import BlendDataNodeTrees, NodeTree


class ToonPaletteFacade:
    def __init__(self, node_groups: BlendDataNodeTrees):
        self.node_groups = node_groups

    def _palettes(self) -> tuple[list[ToonPalette], ToonPalette | None]:
        members: dict[str, list[NodeTree]] = {}
        orphans = []

        for node_tree in filter_node_trees(self.node_groups):
            _, palette_name, group_name = node_tree.name.split("|", 2)

            if palette_name not in members:
                if group_name == "":
                    members[palette_name] = [node_tree]
                else:
                    orphans.append(node_tree)
            else:
                members[palette_name].append(node_tree)

        palettes = [
            ToonPalette(self.node_groups, p[0], p[1:]) for p in members.values()
        ]

        if len(orphans) > 0:
            return palettes, ToonPalette(self.node_groups, None, orphans)
        else:
            return palettes, None

    def _renumber_order(self):
        for index, palette in enumerate(self.palettes()):
            palette.order = index

    def add(self, palette_name: str) -> ToonPalette:
        self._renumber_order()

        name = build_node_tree_name(
            resolve_palette_name(self.node_groups, palette_name), ""
        )
        node_tree = self.node_groups.new(name, "ShaderNodeTree")
        palette = ToonPalette(self.node_groups, node_tree, [])
        palette.init()

        self._renumber_order()

        return palette

    def remove(self, palette_name: str) -> bool:
        if (palette := self.get(palette_name)) is None:
            return False
        else:
            if palette.header is not None:
                self.node_groups.remove(palette.header)

            for node_tree in palette.node_trees:
                self.node_groups.remove(node_tree)

            return True

    def get(self, palette_name: str) -> ToonPalette | None:
        palettes, orphans = self._palettes()

        for palette in palettes:
            if palette.name == palette_name:
                return palette

        return orphans

    def palettes(self) -> list[ToonPalette]:
        palettes, orphans = self._palettes()
        palettes = sorted(palettes, key=lambda p: order_to_key(p.order))

        if orphans is not None:
            palettes.append(orphans)

        return palettes

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
