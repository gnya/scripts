from .base import DataItem, DataCollection
from .socket import SocketLinkedItem

from .item import PaletteItem
from .palette import PaletteGroup, PaletteName, Palette
from .ui import PalettePointer, PaletteUIItem, PaletteUI


__all__ = [
    DataItem,
    DataCollection,
    SocketLinkedItem,
    PaletteItem,
    PaletteGroup,
    PaletteName,
    Palette,
    PalettePointer,
    PaletteUIItem,
    PaletteUI
]


def register():
    from bpy.utils import register_class

    register_class(PaletteItem)
    register_class(PaletteGroup)
    register_class(PaletteName)
    register_class(PaletteUIItem)
    register_class(PaletteUI)


def unregister():
    from bpy.utils import unregister_class

    unregister_class(PaletteItem)
    unregister_class(PaletteGroup)
    unregister_class(PaletteName)
    unregister_class(PaletteUIItem)
    unregister_class(PaletteUI)
