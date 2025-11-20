from __future__ import annotations
from typing import Any, Iterator
from toon.utils import override

import bpy

from bpy.app.handlers import persistent
from bpy.props import CollectionProperty, StringProperty
from bpy.types import NodeTree, PropertyGroup

from toon.props import Palette
from toon.props.group import Entry, EntryBase, Group


class PaletteName(Entry, PropertyGroup):
    id_name: StringProperty()


class PaletteManager(Group, PropertyGroup):
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
            node_tree = bpy.data.node_groups.get(name.id_name)

            yield getattr(node_tree, PaletteManager.PROP_PALETTE_NAME)

    @override
    def _key_to_index(self, key: int | str | EntryBase | Palette) -> int:
        if not isinstance(key, Palette):
            return super()._key_to_index(key)
        else:
            for i, palette in enumerate(self.palettes()):
                if palette == key:
                    return i

            return -1

    @override
    def first(self, key: int | str | EntryBase) -> Palette | None:
        if not isinstance(key, EntryBase):
            result = super().first(key)
        else:
            result = key

        if result is None:
            return None

        node_tree = bpy.data.node_groups.get(result.id_name)

        if node_tree is None:
            return None

        palette = getattr(node_tree, PaletteManager.PROP_PALETTE_NAME)

        return palette if palette.is_available else None

    @override
    def add(self, name: str) -> Palette:
        result = super().add(name)

        node_tree = bpy.data.node_groups.new(
            PaletteManager.NODE_TREE_NAME, 'ShaderNodeTree'
        )
        node_tree.use_fake_user = True
        result.id_name = node_tree.name

        palette = getattr(node_tree, PaletteManager.PROP_PALETTE_NAME)
        palette.is_available = True
        palette.order = len(self.entries) - 1
        palette.name = result.name

        return palette

    @override
    def remove(self, key: int | str | EntryBase | Palette):
        if not isinstance(key, Palette):
            palette = self.first(key)
        else:
            palette = key

        result = super().remove(key)

        if result and palette is not None:
            bpy.data.node_groups.remove(palette.id_data)

            for i, palette in enumerate(self.palettes()):
                palette.order = i

        return result

    @override
    def move(
        self, src_key: int | str | EntryBase | Palette,
        dst_key: int | str | EntryBase | Palette
    ):
        result = super().move(src_key, dst_key)

        if result:
            for i, palette in enumerate(self.palettes()):
                palette.order = i

        return result

    @staticmethod
    @persistent
    def init(dummy: Any = None):
        manager = PaletteManager.instance()
        orders: list[tuple[Palette, NodeTree]] = []

        for node_tree in bpy.data.node_groups:
            palette = getattr(node_tree, PaletteManager.PROP_PALETTE_NAME)

            if palette.is_available:
                orders.append((palette, node_tree))

        manager.entries.clear()
        orders = sorted(orders, key=lambda o: int(o[0].order))

        for palette, node_tree in orders:
            n = manager.entries.add()
            n.name = palette.name
            n.id_name = node_tree.name


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
