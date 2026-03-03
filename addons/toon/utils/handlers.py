from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import bpy
from bpy.app.handlers import depsgraph_update_post, load_post, persistent
from bpy.types import NodeTree, Scene

if TYPE_CHECKING:
    from bpy.types import Depsgraph, DepsgraphUpdate, Object

_object_last_names: dict[int, str] = {}
_node_group_ptrs: list[int] = []

object_rename_post: list[Callable[[Object, str], None]] = []
node_group_update_post: list[Callable[[NodeTree], None]] = []

# NOTE Alternative to `blend_import_post`.
node_group_import_post: list[Callable[[NodeTree], None]] = []


def _poll_object_rename(graph: Depsgraph) -> bool:
    if graph.mode != "VIEWPORT":
        return False

    for update in graph.updates:
        if (
            update.is_updated_geometry
            or update.is_updated_shading
            or update.is_updated_transform
        ):
            return False

    return True


def _object_rename(graph: Depsgraph):
    if not _poll_object_rename(graph):
        return

    global _object_last_names

    last_names: dict[int, str] = {}

    for obj in graph.objects:
        ptr = obj.as_pointer()
        last_name = _object_last_names.get(ptr, "")
        name = obj.original.name
        last_names[ptr] = name

        if name != last_name:
            for callback in object_rename_post:
                callback(obj.original, last_name)

    _object_last_names = last_names


def _poll_node_group_update(graph: Depsgraph) -> bool:
    if graph.mode != "VIEWPORT":
        return False

    for update in graph.updates:
        if update.is_updated_shading:
            return True

    return False


def _node_group_import(update: DepsgraphUpdate):
    global _node_group_ptrs

    if update.is_updated_geometry and update.is_updated_transform:
        for node_tree in bpy.data.node_groups:
            if node_tree.as_pointer() not in _node_group_ptrs:
                for callback in node_group_import_post:
                    callback(node_tree)

    _node_group_ptrs = [n.as_pointer() for n in bpy.data.node_groups]


def _node_group_update(graph: Depsgraph):
    if not _poll_node_group_update(graph):
        return

    for update in graph.updates:
        origin = update.id.original

        if isinstance(origin, Scene):
            _node_group_import(update)
        elif (
            isinstance(origin, NodeTree)
            and origin.type == "SHADER"
            and origin.name != "Shader Nodetree"
        ):
            for callback in node_group_update_post:
                callback(origin)


@persistent
def _depsgraph_update_post(scene: Scene, graph: Depsgraph):
    _object_rename(graph)
    _node_group_update(graph)


@persistent
def _init_global_variables(scene: Scene):
    global _object_last_names
    global _node_group_ptrs

    _object_last_names = {o.as_pointer(): o.name for o in bpy.data.objects}
    _node_group_ptrs = [n.as_pointer() for n in bpy.data.node_groups]


def register_handlers():
    if _depsgraph_update_post not in depsgraph_update_post:
        depsgraph_update_post.append(_depsgraph_update_post)

    if _init_global_variables not in load_post:
        load_post.append(_init_global_variables)


def unregister_handlers():
    if _depsgraph_update_post in depsgraph_update_post:
        depsgraph_update_post.remove(_depsgraph_update_post)

    if _init_global_variables in load_post:
        load_post.remove(_init_global_variables)
