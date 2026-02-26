from typing import Iterator

import bpy

from bpy.types import NodeTree

from .facade_palette import ToonPalette
from .utils import build_node_tree_name
from .utils import filter_node_trees


class ToonPaletteFacade(object):
    @staticmethod
    def add(palette_name: str) -> bool:
        if palette_name == '':
            return False

        name = build_node_tree_name(palette_name, '', True)
        node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')
        node_tree.use_fake_user = True
        node_tree.nodes.new('NodeGroupOutput')

        return True

    @staticmethod
    def remove(palette_name: str) -> bool:
        if palette_name == '':
            return False

        result = False

        name = build_node_tree_name(palette_name, '')

        for node_tree in list(bpy.data.node_groups):
            if node_tree.name.startswith(name):
                bpy.data.node_groups.remove(node_tree)

                result = True

        return result

    @staticmethod
    def get(palette_name: str) -> ToonPalette | None:
        node_trees = list(filter_node_trees(palette_name))

        if len(node_trees) > 0:
            return ToonPalette(node_trees[0], node_trees[1:])
        else:
            return None

    @staticmethod
    def palettes() -> Iterator[ToonPalette]:
        palettes: dict[str, tuple[NodeTree, list[NodeTree]]] = {}
        orphan_groups = []

        for node_tree in filter_node_trees():
            _, palette_name, group_name = node_tree.name.split('|', 2)

            if palette_name not in palettes:
                if group_name == '':
                    palettes[palette_name] = (node_tree, [])
                else:
                    orphan_groups.append(node_tree)
            else:
                palettes[palette_name][1].append(node_tree)

        for palette in palettes.values():
            yield ToonPalette(*palette)

        if len(orphan_groups) > 0:
            yield ToonPalette(None, orphan_groups)
