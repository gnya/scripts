from .palette_entry import PaletteEntry
from .palette import Palette, PaletteGroup, PalettePointer, PaletteSlot
from .toon_settings import ToonSettings


__all__ = [
    PaletteEntry,
    Palette,
    PaletteGroup,
    PalettePointer,
    PaletteSlot,
    ToonSettings
]


classes = (
    PaletteEntry,
    PaletteGroup,
    PaletteSlot,
    Palette,
    ToonSettings
)


def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)
