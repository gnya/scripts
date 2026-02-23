from .node import ToonNodeSettings
from .palette import ToonPaletteColor
from .palette import ToonPaletteGroup
from .palette import ToonPalette
from .palette import ToonPaletteFacade


__all__ = [
    ToonNodeSettings,
    ToonPaletteColor,
    ToonPaletteGroup,
    ToonPalette,
    ToonPaletteFacade
]


classes = (
    ToonNodeSettings,
    ToonPaletteColor,
    ToonPaletteGroup,
    ToonPalette,
    ToonPaletteFacade
)


def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)
