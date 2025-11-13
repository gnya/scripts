from .group import Palette, PaletteEntry, PaletteGroup, PalettePointer, PaletteSlot
from .manager import PaletteName, PaletteManager


__all__ = [
    Palette,
    PaletteEntry,
    PaletteGroup,
    PaletteName,
    PaletteManager,
    PalettePointer,
    PaletteSlot
]


def register():
    from bpy.app import timers
    from bpy.app.handlers import load_post
    from bpy.props import PointerProperty
    from bpy.types import NodeTree, WindowManager
    from bpy.utils import register_class

    from .manager import make_palette_class

    register_class(PaletteEntry)
    register_class(PaletteGroup)
    register_class(PaletteSlot)
    register_class(PaletteName)
    register_class(PaletteManager)

    if not hasattr(PaletteManager, 'PaletteType'):
        PaletteManager.PaletteType = make_palette_class()
        register_class(PaletteManager.PaletteType)
        setattr(
            NodeTree, PaletteManager.PROP_PALETTE_NAME,
            PointerProperty(type=PaletteManager.PaletteType)
        )

    setattr(
        WindowManager, PaletteManager.PROP_NAME,
        PointerProperty(type=PaletteManager)
    )

    if PaletteManager.update not in load_post:
        load_post.append(PaletteManager.update)

    timers.register(PaletteManager.update, first_interval=0.1)


def unregister():
    from bpy.app.handlers import load_post
    from bpy.types import NodeTree, WindowManager
    from bpy.utils import unregister_class

    unregister_class(PaletteEntry)
    unregister_class(PaletteGroup)
    unregister_class(PaletteSlot)
    unregister_class(PaletteName)
    unregister_class(PaletteManager)

    if hasattr(PaletteManager, 'PaletteType'):
        unregister_class(PaletteManager.PaletteType)
        delattr(
            NodeTree, PaletteManager.PROP_PALETTE_NAME
        )

    delattr(WindowManager, PaletteManager.PROP_NAME)

    if PaletteManager.update in load_post:
        load_post.remove(PaletteManager.update)
