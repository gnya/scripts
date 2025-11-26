from typing import Callable

import bpy

from bpy.app.handlers import load_post, persistent
from bpy.types import Property, Struct

_msgbus_owner = object()
_msgbus_subscribers = {}


def subscribe_rna(
    key: Property | Struct | tuple[Struct, str],
    notify: Callable[[], None],
    args: tuple[...] = ()
) -> bool:
    if key in _msgbus_subscribers:
        return False

    bpy.msgbus.subscribe_rna(
        key=key,
        owner=_msgbus_owner,
        args=args,
        notify=notify
    )
    _msgbus_subscribers[key] = (notify, args)

    return True


def unsubscribe_rna_all():
    bpy.msgbus.clear_by_owner(_msgbus_owner)
    _msgbus_subscribers.clear()


@persistent
def _subscribe_rna(dummy: str):
    bpy.msgbus.clear_by_owner(_msgbus_owner)

    for key, (notify, args) in _msgbus_subscribers.items():
        bpy.msgbus.subscribe_rna(
            key=key,
            owner=_msgbus_owner,
            args=args,
            notify=notify
        )


def register():
    if _subscribe_rna not in load_post:
        load_post.append(_subscribe_rna)


def unregister():
    unsubscribe_rna_all()

    if _subscribe_rna in load_post:
        load_post.remove(_subscribe_rna)
