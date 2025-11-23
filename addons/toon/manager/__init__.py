from .manager import PaletteManager


__all__ = [
    PaletteManager
]


def register():
    from bpy.props import PointerProperty
    from bpy.types import NodeTree, WindowManager
    from bpy.utils import register_class

    from .palette import ManagablePalette

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


def unregister():
    from bpy.types import NodeTree, WindowManager
    from bpy.utils import unregister_class

    from .palette import ManagablePalette

    unregister_class(ManagablePalette)
    delattr(NodeTree, PaletteManager.PROP_PALETTE_NAME)

    unregister_class(PaletteManager)
    delattr(WindowManager, PaletteManager.PROP_NAME)
