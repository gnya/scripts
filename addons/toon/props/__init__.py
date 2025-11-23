from .id_key import IDKey
from .palette_entry import PaletteEntry
from .palette import Palette
from .palette import PaletteGroup
from .palette import PalettePointer
from .palette import PaletteSlot
from .toon_settings import ToonSettings


__all__ = [
    IDKey,
    PaletteEntry,
    Palette,
    PaletteGroup,
    PalettePointer,
    PaletteSlot,
    ToonSettings
]


classes = (
    IDKey,
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
