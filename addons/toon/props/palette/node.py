from __future__ import annotations

from typing import TYPE_CHECKING

import bpy
from bpy.app.handlers import persistent, redo_post, undo_post
from bpy.props import BoolProperty, CollectionProperty, PointerProperty
from bpy.types import PropertyGroup, WindowManager

from toon.palette import get_palettes
from toon.utils import node_group_import_post

if TYPE_CHECKING:
    from bpy.types import Scene

    from toon.palette import ToonPalette


class ToonPaletteSearchGroup(PropertyGroup):
    def init(self, name_full: str):
        self.name = name_full


class ToonPaletteSearchPalette(PropertyGroup):
    groups: CollectionProperty(type=ToonPaletteSearchGroup)

    def init(self, palette: ToonPalette):
        self.name = palette.name_full

        for group in palette.groups():
            state = self.groups.add()
            state.init(group.name_full)


class ToonPaletteSearchIndex(PropertyGroup):
    PROP_NAME = "toon_palette_node_state"

    palettes: CollectionProperty(type=ToonPaletteSearchPalette)

    orphans: CollectionProperty(type=ToonPaletteSearchGroup)

    update_requested: BoolProperty(default=True)

    def update(self):
        if not self.update_requested:
            return

        self.palettes.clear()
        self.orphans.clear()

        for palette in get_palettes():
            if palette.is_orphens:
                for group in palette.groups():
                    state = self.orphans.add()
                    state.init(group.name_full)
            else:
                state = self.palettes.add()
                state.init(palette)

        self.update_requested = False

    @staticmethod
    def instance() -> ToonPaletteSearchIndex:
        id = bpy.context.window_manager

        return getattr(id, ToonPaletteSearchIndex.PROP_NAME)

    @staticmethod
    def request_update():
        states = ToonPaletteSearchIndex.instance()
        states.update_requested = True

    @staticmethod
    def current() -> ToonPaletteSearchIndex:
        states = ToonPaletteSearchIndex.instance()
        states.update()

        return states

    @staticmethod
    @persistent
    def _sync_state(object: Scene):
        ToonPaletteSearchIndex.request_update()

    @staticmethod
    def register():
        setattr(
            WindowManager,
            ToonPaletteSearchIndex.PROP_NAME,
            PointerProperty(type=ToonPaletteSearchIndex),
        )

        redo_post.append(ToonPaletteSearchIndex._sync_state)
        undo_post.append(ToonPaletteSearchIndex._sync_state)
        node_group_import_post.append(ToonPaletteSearchIndex._sync_state)

    @staticmethod
    def unregister():
        delattr(WindowManager, ToonPaletteSearchIndex.PROP_NAME)

        redo_post.remove(ToonPaletteSearchIndex._sync_state)
        undo_post.remove(ToonPaletteSearchIndex._sync_state)
        node_group_import_post.remove(ToonPaletteSearchIndex._sync_state)
