from __future__ import annotations
from typing import Any, Iterator

import bpy

from bpy.app.handlers import persistent
from bpy.props import CollectionProperty
from bpy.types import NodeTree, PropertyGroup

from toon.utils.group import EntryBase

from .group import Palette


class PaletteName(PropertyGroup):
    pass


class PaletteManager(PropertyGroup):
    NODE_TREE_NAME = '.TOON_PALETTE'
    PROP_NAME = 'toon_palette_manager'
    PROP_PALETTE_NAME = 'toon_palette'

    names: CollectionProperty(type=PaletteName)

    @staticmethod
    def instance() -> PaletteManager:
        wm = bpy.context.window_manager

        return getattr(wm, PaletteManager.PROP_NAME)

    @staticmethod
    def entry_names() -> Any:
        return PaletteManager.instance().names

    @staticmethod
    def entries() -> Iterator[Palette]:
        for node_tree in bpy.data.node_groups:
            palette = getattr(
                node_tree, PaletteManager.PROP_PALETTE_NAME
            )

            if palette.is_available:
                yield palette

    @staticmethod
    @persistent
    def update(dummy: Any = None):
        names = PaletteManager.entry_names()
        names.clear()

        for palette in PaletteManager.entries():
            names.add().name = palette.name

    @staticmethod
    def add(name: str) -> Palette:
        node_tree = bpy.data.node_groups.new(
            PaletteManager.NODE_TREE_NAME, 'ShaderNodeTree'
        )
        node_tree.use_fake_user = True

        palette = getattr(
            node_tree, PaletteManager.PROP_PALETTE_NAME
        )
        palette.is_available = True
        palette.name = name

        PaletteManager.update()

        return palette

    @staticmethod
    def remove(key: Palette):
        bpy.data.node_groups.remove(key.id_data)

        PaletteManager.update()

    @staticmethod
    def move():
        pass

    @staticmethod
    def get_entry(key: str | NodeTree) -> Palette | None:
        if isinstance(key, NodeTree):
            palette = getattr(
                key, PaletteManager.PROP_PALETTE_NAME
            )

            return palette if palette.is_available else None

        for palette in PaletteManager.entries():
            if palette.name == key:
                return palette

        return None


def make_palette_class():
    def _parent(self: Any) -> tuple[list[str], list[EntryBase]]:
        names, entries = [], []

        for palette in PaletteManager.entries():
            names.append(palette.name)
            entries.append(palette)

        return names, entries

    return type('_Palette', (Palette,), {
        'parent': _parent, 'on_rename': PaletteManager.update
    })
