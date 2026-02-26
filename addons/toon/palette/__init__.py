from __future__ import annotations
from typing import Iterator

import bpy

from bpy.types import NodeTree

from .utils import is_palette
from .utils import build_node_tree_name
from .utils import get_palette_name
from .utils import get_group_name
from .utils import filter_node_trees


__all__ = [
    get_palette_name,
    get_group_name
]


class ToonPaletteColor(object):
    def __init__(self, index: int, node_tree: NodeTree) -> None:
        self.socket_index = index
        self.node_tree = node_tree

    @property
    def name(self) -> str:
        return self.node_tree.outputs[self.socket_index].name

    @name.setter
    def name(self, value: str):
        self.node_tree.outputs[self.socket_index].name = value


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

    @staticmethod
    def from_node_tree(node_tree: NodeTree) -> ToonPaletteGroup | None:
        if is_palette(node_tree):
            return ToonPaletteGroup(node_tree)
        else:
            return None


class ToonPalette(object):
    def __init__(self, header: NodeTree, node_trees: list[NodeTree]):
        self.header = header
        self.node_trees = node_trees

    @property
    def name(self) -> str:
        return get_palette_name(self.header)

    @name.setter
    def name(self, value: str):
        if value == self.name:
            return
        elif value == '':
            value = 'Palette'
        else:
            value = value.replace('|', '_')

        name = build_node_tree_name(self.name, '')
        new_name = build_node_tree_name(value, '', True)

        self.header.name = self.header.name.replace(name, new_name, 1)

        for node_tree in self.node_trees:
            node_tree.name = node_tree.name.replace(name, new_name, 1)

    def add(self, group_name: str) -> bool:
        if group_name == '':
            return False

        name = build_node_tree_name(self.name, group_name)
        node_tree = bpy.data.node_groups.new(name, 'ShaderNodeTree')
        node_tree.use_fake_user = True

        self.node_trees.append(node_tree)

        return True

    def remove(self, group_name: str) -> bool:
        if group_name == '':
            return False

        name = build_node_tree_name(self.name, group_name)

        for node_tree in self.node_trees:
            if node_tree.name == name:
                bpy.data.node_groups.remove(node_tree)

                return True

        return False

    def get(self, group_name: str) -> ToonPaletteGroup | None:
        for node_tree in self.node_trees:
            if node_tree.name.split('|', 2)[2] == group_name:
                return ToonPaletteGroup(node_tree)

        return None

    def groups(self) -> Iterator[ToonPaletteGroup]:
        for node_tree in self.node_trees:
            yield ToonPaletteGroup(node_tree)

    @staticmethod
    def from_node_tree(node_tree: NodeTree) -> ToonPalette | None:
        if is_palette(node_tree):
            names = node_tree.name.split('|', 2)
            node_trees = list(filter_node_trees(names[1]))

            return ToonPalette(node_trees[0], node_trees[1:])
        else:
            return None


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
