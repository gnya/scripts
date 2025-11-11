from .socket import SocketEntry

from .entry import PaletteEntry
from .palette import PaletteGroup, PaletteName, Palette
from .ui import PalettePointer, PaletteSlot, PaletteUI


__all__ = [
    SocketEntry,
    PaletteEntry,
    PaletteGroup,
    PaletteName,
    Palette,
    PalettePointer,
    PaletteSlot,
    PaletteUI
]


def register():
    from bpy.utils import register_class

    register_class(PaletteEntry)
    register_class(PaletteGroup)
    register_class(PaletteName)
    register_class(PaletteSlot)
    register_class(PaletteUI)


def unregister():
    from bpy.utils import unregister_class

    unregister_class(PaletteEntry)
    unregister_class(PaletteGroup)
    unregister_class(PaletteName)
    unregister_class(PaletteSlot)
    unregister_class(PaletteUI)
