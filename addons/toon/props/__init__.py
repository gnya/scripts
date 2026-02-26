from .node import ToonNodeSettings
from .palette_node import ToonPaletteSearchGroup
from .palette_node import ToonPaletteSearchPalette
from .palette_node import ToonPaletteSearchIndex
from .palette_panel import ToonPaletteViewSettings
from .palette_panel import ToonPaletteUIItem
from .palette_panel import ToonPaletteUIPaletteState
from .palette_panel import ToonPaletteUIState


__all__ = [
    ToonNodeSettings,
    ToonPaletteSearchGroup,
    ToonPaletteSearchPalette,
    ToonPaletteSearchIndex,
    ToonPaletteViewSettings,
    ToonPaletteUIItem,
    ToonPaletteUIPaletteState,
    ToonPaletteUIState
]


classes = (
    ToonNodeSettings,
    ToonPaletteSearchGroup,
    ToonPaletteSearchPalette,
    ToonPaletteSearchIndex,
    ToonPaletteViewSettings,
    ToonPaletteUIItem,
    ToonPaletteUIPaletteState,
    ToonPaletteUIState
)


def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)
