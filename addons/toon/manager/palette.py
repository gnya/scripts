from toon.utils import override

from toon.props import Palette
from toon.props.group import EntryBase

from .manager import PaletteManager


class ManagablePalette(Palette):
    @override
    def parent(self) -> tuple[list[str], list[EntryBase]]:
        manager = PaletteManager.instance()
        names, entries = [], []

        for palette in manager.palettes():
            names.append(palette.name)
            entries.append(palette)

        return names, entries
