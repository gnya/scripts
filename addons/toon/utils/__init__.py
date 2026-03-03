from .handlers import node_group_import_post, node_group_update_post, object_rename_post
from .lock import list_pids, register_pid, unregister_pid
from .naming import unique_name
from .node import (
    all_node_itr,
    all_node_users_itr,
    node_itr,
    node_tree_itr,
    remove_nodes,
    search_node,
)
from .range import slice_itr, within
from .socket import NodeLinkRebinder, change_socket_type
from .typing import override

__all__ = [
    list_pids,
    register_pid,
    unregister_pid,
    node_itr,
    node_tree_itr,
    all_node_itr,
    all_node_users_itr,
    remove_nodes,
    search_node,
    change_socket_type,
    override,
    slice_itr,
    within,
    unique_name,
    object_rename_post,
    node_group_update_post,
    node_group_import_post,
    NodeLinkRebinder,
]


def register():
    from .handlers import register_handlers

    register_handlers()


def unregister():
    from .handlers import unregister_handlers

    unregister_handlers()
