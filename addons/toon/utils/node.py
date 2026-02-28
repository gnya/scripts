from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

import bpy
from bpy.types import NodeTree

if TYPE_CHECKING:
    from bpy.types import ID, Node, NodeSocket


def node_itr(node_tree: NodeTree, type: str = "") -> Iterator[Node]:
    if not type:
        for node in node_tree.nodes:
            yield node
    else:
        for node in node_tree.nodes:
            if node.bl_idname == type:
                yield node


def node_tree_itr(collection: Iterator[ID]) -> Iterator[Node]:
    for data in collection:
        node_tree = getattr(data, "node_tree", data)

        if not isinstance(node_tree, NodeTree):
            continue

        yield from node_itr(node_tree)


def all_node_itr() -> Iterator[Node]:
    yield from node_tree_itr(bpy.data.node_groups)
    yield from node_tree_itr(bpy.data.materials)
    yield from node_tree_itr(bpy.data.scenes)
    yield from node_tree_itr(bpy.data.linestyles)
    yield from node_tree_itr(bpy.data.lights)
    yield from node_tree_itr(bpy.data.worlds)
    yield from node_tree_itr(bpy.data.textures)


def all_node_users_itr(node_tree: NodeTree) -> Iterator[Node]:
    for node in all_node_itr():
        if node_tree == getattr(node, "node_tree", None):
            yield node


def remove_nodes(root: NodeSocket):
    if len(root.links) != 1:
        return

    node = root.links[0].from_node

    for input in node.inputs:
        remove_nodes(input)

    root.id_data.nodes.remove(node)


def search_node(root: NodeSocket, type: str) -> Node | None:
    if len(root.links) != 1:
        return

    node = root.links[0].from_node

    if node.bl_idname == type:
        return node

    for input in node.inputs:
        node = search_node(input, type)

        if node is not None:
            return node

    return None
