from __future__ import annotations
from typing import Any, Iterator
from toon.utils import override

import bpy

from bpy.app.handlers import persistent
from bpy.props import CollectionProperty, StringProperty
from bpy.types import NodeTree, PropertyGroup

from toon.utils.group import EntryBase

from .group import Palette


class PaletteName(PropertyGroup):
    node_tree_name: StringProperty()


class PaletteManager(PropertyGroup):
    NODE_TREE_NAME = '.TOON_PALETTE'
    PROP_NAME = 'toon_palette_manager'
    PROP_PALETTE_NAME = 'toon_palette'

    entries: CollectionProperty(type=PaletteName)

    @staticmethod
    def instance() -> PaletteManager:
        wm = bpy.context.window_manager

        return getattr(wm, PaletteManager.PROP_NAME)

    def palettes(self) -> Iterator[Palette]:
        for name in self.entries:
            node_tree = bpy.data.node_groups.get(name.node_tree_name)

            yield getattr(node_tree, PaletteManager.PROP_PALETTE_NAME)

    def _key_to_index(self, key: int | str | Palette) -> int:
        if isinstance(key, int):
            if key < 0:
                return len(self.entries) + key
            else:
                return key
        elif isinstance(key, str):
            return self.entries.find(key)
        else:
            return self.entries.find(key.name)

    def find(self, key: str | Palette) -> int:
        return self._key_to_index(key)

    def add(self, name: str) -> Palette:
        node_tree = bpy.data.node_groups.new(
            PaletteManager.NODE_TREE_NAME, 'ShaderNodeTree'
        )
        node_tree.use_fake_user = True

        entry = self.entries.add()
        entry.name = name
        entry.node_tree_name = node_tree.name

        palette = getattr(
            node_tree, PaletteManager.PROP_PALETTE_NAME
        )
        palette.is_available = True
        palette.order = len(self.entries)
        palette.name = name  # This line calls `PaletteManager.init()`.

        return palette

    def remove(self, key: int | str | Palette):
        index = self._key_to_index(key)

        if index < 0 or index >= len(self.entries):
            return False

        self.entries.remove(index)

        bpy.data.node_groups.remove(key.id_data)

        return True

    def move(self, src_key: int | str | Palette, dst_key: int | str | Palette):
        src_index = self._key_to_index(src_key)
        dst_index = self._key_to_index(dst_key)

        if src_index == dst_index:
            return False
        elif src_index < 0 or src_index >= len(self.entries):
            return False
        elif dst_index < 0 or dst_index >= len(self.entries):
            return False

        self.entries.move(src_index, dst_index)

        i = 0

        for palette in self.palettes():
            palette.order = i
            i += 1

        return True

    def get_entry(self, key: str | NodeTree) -> Palette | None:
        if isinstance(key, NodeTree):
            palette = getattr(
                key, PaletteManager.PROP_PALETTE_NAME
            )

            return palette if palette.is_available else None

        for palette in self.palettes():
            if palette.name == key:
                return palette

        return None

    @staticmethod
    @persistent
    def init(dummy: Any = None):
        manager = PaletteManager.instance()
        orders: list[tuple[int, str, str]] = []

        for node_tree in bpy.data.node_groups:
            palette = getattr(node_tree, PaletteManager.PROP_PALETTE_NAME)

            if palette.is_available:
                orders.append((palette.order, palette.name, node_tree.name))

        manager.entries.clear()
        orders = sorted(orders, key=lambda o: o[0])

        for _, name, node_tree_name in orders:
            n = manager.entries.add()
            n.name = name
            n.node_tree_name = node_tree_name


class ManagablePalette(Palette):
    @override
    def parent(self: Any) -> tuple[list[str], list[EntryBase]]:
        manager = PaletteManager.instance()
        names, entries = [], []

        for palette in manager.palettes():
            names.append(palette.name)
            entries.append(palette)

        return names, entries

    @override
    def on_rename(self):
        PaletteManager.init()
