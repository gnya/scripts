from __future__ import annotations
from toon.utils import override

import bpy

from bpy.props import CollectionProperty
from bpy.types import NodeTree, PropertyGroup

from toon.props import Palette
from toon.props.group import EntryBase, GroupBase
from toon.utils import make_unique_name

from .id import PaletteID


class PaletteManager(GroupBase[Palette], PropertyGroup):
    NODE_TREE_NAME = '.TOON_PALETTE'
    PROP_NAME = 'toon_palette_manager'
    PROP_PALETTE_NAME = 'toon_palette'

    ids_cache: CollectionProperty(type=PaletteID)

    @staticmethod
    def instance() -> PaletteManager:
        wm = bpy.context.window_manager

        return getattr(wm, PaletteManager.PROP_NAME)

    def _key_to_index(self, key: int | str | Palette) -> int:
        if isinstance(key, int):
            if key < 0:
                return len(self.ids_cache) + key
            else:
                return key
        elif isinstance(key, str):
            return self.ids_cache.find(key)
        elif key.id_data.library is None:
            return self.ids_cache.find(key.name)
        else:
            id_lib = key.id_data.library.filepath
            name = f'{key.name} [{id_lib}]'

            return self.ids_cache.find(name)

    def from_data(self, data: NodeTree, available_only: bool = True) -> Palette | None:
        palette = getattr(data, PaletteManager.PROP_PALETTE_NAME)

        if not palette.is_available and available_only:
            return None

        return palette

    def palettes(self) -> list[Palette]:
        orders: list[Palette] = []

        for node_tree in bpy.data.node_groups:
            palette = self.from_data(node_tree)

            if palette is not None:
                orders.append(palette)

        return sorted(orders, key=lambda o: int(o.order))

    def update_ids(self):
        self.ids_cache.clear()

        for palette in self.palettes():
            node_tree = palette.id_data
            id = self.ids_cache.add()
            id.id_name = node_tree.name

            if node_tree.library is None:
                id.name = palette.name
            else:
                id_lib = node_tree.library.filepath
                id.id_lib = id_lib
                id.name = f'{palette.name} [{id_lib}]'

    @override
    def first(self, key: int | str) -> Palette | None:
        self.update_ids()

        index = self._key_to_index(key)

        if index < 0 or index >= len(self.ids_cache):
            return None

        id = self.ids_cache[index]
        node_tree = bpy.data.node_groups[id.id_key()]

        return self.from_data(node_tree)

    @override
    def find(self, key: str | Palette) -> int:
        self.update_ids()

        return self._key_to_index(key)

    @override
    def add(self, name: str) -> Palette:
        self.update_ids()

        node_tree = bpy.data.node_groups.new(PaletteManager.NODE_TREE_NAME, 'ShaderNodeTree')
        node_tree.use_fake_user = True
        palette = self.from_data(node_tree, available_only=False)

        if palette is None:
            raise RuntimeError(f'{node_tree.name}: Failed to add a palette.')

        name = make_unique_name(name, self.ids_cache.keys())
        palette.is_available = True
        palette.order = len(self.ids_cache)
        palette.name = name

        return palette

    @override
    def remove(self, key: int | str | Palette) -> bool:
        if not isinstance(key, Palette):
            palette = self.first(key)
        else:
            palette = key

        if palette is None:
            return False

        bpy.data.node_groups.remove(palette.id_data)

        for i, palette in enumerate(self.palettes()):
            palette.order = i

        return True

    @override
    def clear(self) -> bool:
        for palette in self.palettes():
            bpy.data.node_groups.remove(palette.id_data)

        return True

    @override
    def move(self, src_key: int | str | Palette, dst_key: int | str | Palette) -> bool:
        self.update_ids()

        src_index = self._key_to_index(src_key)
        dst_index = self._key_to_index(dst_key)

        if src_index == dst_index:
            return False
        elif src_index < 0 or src_index >= len(self.ids_cache):
            return False
        elif dst_index < 0 or dst_index >= len(self.ids_cache):
            return False

        for i, palette in enumerate(self.palettes()):
            if i == src_index:
                palette.order = dst_index
            elif i == dst_index:
                palette.order = src_index

        return True


class ManagablePalette(Palette):
    @override
    def parent(self) -> tuple[list[str], list[EntryBase]]:
        manager = PaletteManager.instance()
        names, entries = [], []

        for palette in manager.palettes():
            names.append(palette.name)
            entries.append(palette)

        return names, entries
