from .manager import PaletteName, PaletteManager


__all__ = [
    PaletteName,
    PaletteManager
]


def register():
    from bpy.app import timers
    from bpy.app.handlers import load_post
    from bpy.props import PointerProperty
    from bpy.types import NodeTree, WindowManager
    from bpy.utils import register_class

    from .manager import ManagablePalette

    register_class(PaletteName)

    register_class(ManagablePalette)
    setattr(
        NodeTree, PaletteManager.PROP_PALETTE_NAME,
        PointerProperty(type=ManagablePalette)
    )

    register_class(PaletteManager)
    setattr(
        WindowManager, PaletteManager.PROP_NAME,
        PointerProperty(type=PaletteManager)
    )

    if PaletteManager.init not in load_post:
        load_post.append(PaletteManager.init)

    timers.register(PaletteManager.init, first_interval=0.1)


def unregister():
    from bpy.app.handlers import load_post
    from bpy.types import NodeTree, WindowManager
    from bpy.utils import unregister_class

    from .manager import ManagablePalette

    unregister_class(PaletteName)

    unregister_class(ManagablePalette)
    delattr(NodeTree, PaletteManager.PROP_PALETTE_NAME)

    unregister_class(PaletteManager)
    delattr(WindowManager, PaletteManager.PROP_NAME)

    if PaletteManager.init in load_post:
        load_post.remove(PaletteManager.init)
