from typing import Callable

import bpy

from bpy.app.handlers import depsgraph_update_post, load_post, persistent
from bpy.types import Depsgraph, NodeTree, Object, Scene

object_rename_post: list[Callable[[Object, str], None]] = []
node_tree_update_post: list[Callable[[NodeTree], None]] = []

_object_last_names: dict[int, str] = {}


def _poll_object_rename(graph: Depsgraph) -> bool:
    if graph.mode != 'VIEWPORT':
        return False

    for update in graph.updates:
        if (
            update.is_updated_geometry or
            update.is_updated_shading or
            update.is_updated_transform
        ):
            return False

    return True


def _object_rename(graph: Depsgraph):
    if not _poll_object_rename(graph):
        return

    global _object_last_names

    last_names: dict[int, str] = {}

    for o in graph.objects:
        p = o.as_pointer()
        last_name = _object_last_names.get(p, '')
        name = o.original.name
        last_names[p] = name

        if name == last_name:
            continue

        for callback in object_rename_post:
            callback(o.original, last_name)

    _object_last_names = last_names


def _poll_node_tree_update(graph: Depsgraph) -> bool:
    if graph.mode != 'VIEWPORT':
        return False

    for update in graph.updates:
        if update.is_updated_shading:
            return True

    return False


def _node_tree_update(graph: Depsgraph):
    if not _poll_node_tree_update(graph):
        return

    for update in graph.updates:
        origin = update.id.original

        if not isinstance(update.id, NodeTree):
            continue
        if origin.type != 'SHADER':
            continue
        elif origin.name == 'Shader Nodetree':
            continue

        for callback in node_tree_update_post:
            callback(origin)


@persistent
def _depsgraph_update_post(scene: Scene, graph: Depsgraph):
    _object_rename(graph)
    _node_tree_update(graph)


@persistent
def _init_object_rename(scene: Scene):
    _object_last_names.clear()

    for obj in bpy.data.objects:
        _object_last_names[obj.as_pointer()] = obj.name


def register():
    if _depsgraph_update_post not in depsgraph_update_post:
        depsgraph_update_post.append(_depsgraph_update_post)

    if _init_object_rename not in load_post:
        load_post.append(_init_object_rename)


def unregister():
    if _depsgraph_update_post in depsgraph_update_post:
        depsgraph_update_post.remove(_depsgraph_update_post)

    if _init_object_rename in load_post:
        load_post.remove(_init_object_rename)
