from __future__ import annotations
from typing import Any, Iterator
from toon.utils import override

import bpy

from bpy.app.handlers import persistent
from bpy.props import CollectionProperty, StringProperty
from bpy.types import NodeTree, PropertyGroup

from toon.json import decode_palette, encode_node_tree
from toon.props import Palette
from toon.utils.group import Entry, EntryBase, Group


class PaletteName(Entry, PropertyGroup):
    node_tree_name: StringProperty()


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
            node_tree = bpy.data.node_groups.get(name.node_tree_name)

            yield getattr(node_tree, PaletteManager.PROP_PALETTE_NAME)

    def get_entry(self, key: int | str | EntryBase | NodeTree) -> Palette | None:
        if not isinstance(key, NodeTree):
            result = super().get_entry(key)

            if result is None:
                return None

            node_tree = bpy.data.node_groups.get(result.node_tree_name)

            if node_tree is None:
                return None

            key = node_tree

        palette = getattr(key, PaletteManager.PROP_PALETTE_NAME)

        return palette if palette.is_available else None

    @override
    def add(self, name: str) -> Palette:
        result = super().add(name)

        node_tree = bpy.data.node_groups.new(
            PaletteManager.NODE_TREE_NAME, 'ShaderNodeTree'
        )
        node_tree.use_fake_user = True
        result.node_tree_name = node_tree.name

        palette = getattr(node_tree, PaletteManager.PROP_PALETTE_NAME)
        palette.is_available = True
        palette.order = len(self.entries) - 1
        palette.name = result.name

        return palette

    def add_by_node_tree(self, node_tree: NodeTree) -> Palette:
        palette = self.add(node_tree.name)

        data = encode_node_tree(node_tree)
        decode_palette(data, palette)
        palette.update_slots()

        return palette

    @override
    def remove(self, key: int | str | EntryBase):
        palette = self.get_entry(key)
        result = super().remove(key)

        if result and palette is not None:
            bpy.data.node_groups.remove(palette.id_data)

            for i, palette in enumerate(self.palettes()):
                palette.order = i

        return result

    @override
    def move(self, src_key: int | str | EntryBase, dst_key: int | str | EntryBase):
        result = super().move(src_key, dst_key)

        if result:
            for i, palette in enumerate(self.palettes()):
                palette.order = i

        return result

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
