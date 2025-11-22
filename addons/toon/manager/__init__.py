from .id import PaletteID
from .manager import PaletteManager


__all__ = [
    PaletteID,
    PaletteManager
]


def register():
    from bpy.props import PointerProperty
    from bpy.types import NodeTree, WindowManager
    from bpy.utils import register_class

    from .manager import ManagablePalette

    register_class(PaletteID)

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

    from .manager import ManagablePalette

    unregister_class(PaletteID)

    unregister_class(ManagablePalette)
    delattr(NodeTree, PaletteManager.PROP_PALETTE_NAME)

    unregister_class(PaletteManager)
    delattr(WindowManager, PaletteManager.PROP_NAME)
