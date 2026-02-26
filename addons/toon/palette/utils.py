from typing import Iterator

import bpy

from bpy.types import NodeTree
from re import sub


NODE_TREE_NAME = '.ToonPalette'


def is_palette(node_tree: NodeTree):
    names = node_tree.name.split('|', 2)

    return len(names) == 3 and names[0] == NODE_TREE_NAME


def get_palette_name(node_tree: NodeTree) -> str:
    if is_palette(node_tree):
        return node_tree.name.split('|', 2)[1]
    else:
        return ''


def get_group_name(node_tree: NodeTree) -> str:
    if is_palette(node_tree):
        return node_tree.name.split('|', 2)[2]
    else:
        return ''


def filter_node_trees(palette_name: str = '') -> Iterator[NodeTree]:
    for node_tree in bpy.data.node_groups:
        if is_palette(node_tree):
            if palette_name == '':
                yield node_tree
            else:
                names = node_tree.name.split('|', 2)

                if names[1] == palette_name:
                    yield node_tree


def _group_names() -> list[str]:
    group_names = []

    for node_tree in filter_node_trees():
        names = node_tree.name.split('|', 2)

        if names[2] == '':
            group_names.append(names[1])

    return group_names


def _make_unique_name(name: str, names: list[str]) -> str:
    base = sub(r'.\d{3}$', '', name)
    i = 1

    while name in names:
        name = f'{base}.{i:03d}'
        i += 1

    return name


def build_node_tree_name(palette_name: str, group_name: str, unique: bool = False) -> str:
    if unique:
        palette_name = _make_unique_name(palette_name, _group_names())

    return '|'.join([NODE_TREE_NAME, palette_name, group_name])
