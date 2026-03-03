from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.types import Menu

from toon.ops import (
    VIEW3D_OT_toon_palette_add,
    VIEW3D_OT_toon_palette_add_group,
    VIEW3D_OT_toon_palette_copy,
    VIEW3D_OT_toon_palette_merge,
    VIEW3D_OT_toon_palette_merge_group,
    VIEW3D_OT_toon_palette_move,
    VIEW3D_OT_toon_palette_paste,
    VIEW3D_OT_toon_palette_remove_group,
)
from toon.palette import mergable_groups, mergable_palettes
from toon.utils import override

if TYPE_CHECKING:
    from bpy.types import Context

    from toon.props import ToonPaletteUIPaletteState


class VIEW3D_MT_toon_palette_add(Menu):
    bl_idname = "VIEW3D_MT_toon_palette_add"
    bl_label = "Add Palette"

    @override
    def draw(self, context: Context):
        layout = self.layout

        layout.operator(
            VIEW3D_OT_toon_palette_add.bl_idname, text="Add Empty Palette", icon="ADD"
        )
        layout.operator(
            VIEW3D_OT_toon_palette_paste.bl_idname,
            text="Paste Palette",
            icon="PASTEDOWN",
        )
        layout.separator()


def _draw_toon_palette_merge(
    self: Menu, state: ToonPaletteUIPaletteState, overwrite: bool
):
    layout = self.layout

    src_palette = state.palette_data()

    if src_palette is None:
        layout.label(text="No merge source found.", icon="INFO")

        return

    mergables = list(mergable_palettes(src_palette))

    if len(mergables) == 0:
        layout.label(text="No merge target found.", icon="INFO")

        return

    for dst_palette in mergables:
        o = layout.operator(
            VIEW3D_OT_toon_palette_merge.bl_idname,
            text=f"{src_palette.name} → {dst_palette.name}",
        )
        o.palette_name_full = dst_palette.name_full
        o.overwrite = overwrite


def _draw_toon_palette_merge_group(
    self: Menu, state: ToonPaletteUIPaletteState, overwrite: bool
):
    layout = self.layout

    src_palette = state.palette_data()
    src_group = state.active_group_data()

    if src_palette is None or src_group is None:
        layout.label(text="No merge source found.", icon="INFO")

        return

    mergables = list(mergable_groups(src_palette, src_group))

    if len(mergables) == 0:
        layout.label(text="No merge target found.", icon="INFO")

        return

    for dst_palette, dst_group in mergables:
        dst_palette_name = "" if dst_palette.is_orphens else dst_palette.name
        o = layout.operator(
            VIEW3D_OT_toon_palette_merge_group.bl_idname,
            text=f"{src_group.name} → {dst_palette_name} / {dst_group.name}",
        )
        o.palette_name_full = dst_palette.name_full
        o.group_name_full = dst_group.name_full
        o.overwrite = overwrite


class VIEW3D_MT_toon_palette_merge(Menu):
    bl_idname = "VIEW3D_MT_toon_palette_merge"
    bl_label = "Merge Palette"

    @override
    def draw(self, context: Context):
        _draw_toon_palette_merge(self, context.palette_state, False)


class VIEW3D_MT_toon_palette_merge_overwrite(Menu):
    bl_idname = "VIEW3D_MT_toon_palette_merge_overwrite"
    bl_label = "Merge Palette (Overwrite)"

    @override
    def draw(self, context: Context):
        _draw_toon_palette_merge(self, context.palette_state, True)


class VIEW3D_MT_toon_palette_merge_group(Menu):
    bl_idname = "VIEW3D_MT_toon_palette_merge_group"
    bl_label = "Merge Group"

    @override
    def draw(self, context: Context):
        _draw_toon_palette_merge_group(self, context.palette_state, False)


class VIEW3D_MT_toon_palette_merge_group_overwrite(Menu):
    bl_idname = "VIEW3D_MT_toon_palette_merge_group_overwrite"
    bl_label = "Merge Group (Overwrite)"

    @override
    def draw(self, context: Context):
        _draw_toon_palette_merge_group(self, context.palette_state, True)


class VIEW3D_MT_toon_palette(Menu):
    bl_idname = "VIEW3D_MT_toon_palette"
    bl_label = "Palette Specials"

    @override
    def draw(self, context: Context):
        layout = self.layout

        layout.operator(
            VIEW3D_OT_toon_palette_copy.bl_idname, text="Copy Palette", icon="COPYDOWN"
        )
        layout.separator()
        o = layout.operator(
            VIEW3D_OT_toon_palette_move.bl_idname, text="Move Palette", icon="TRIA_UP"
        )
        o.direction = "UP"
        o = layout.operator(
            VIEW3D_OT_toon_palette_move.bl_idname, text="Move Palette", icon="TRIA_DOWN"
        )
        o.direction = "DOWN"
        layout.separator()
        layout.menu(VIEW3D_MT_toon_palette_merge.bl_idname, text="Merge Palette")
        layout.menu(
            VIEW3D_MT_toon_palette_merge_overwrite.bl_idname,
            text="Merge Palette (Overwrite)",
        )


class VIEW3D_MT_toon_palette_group(Menu):
    bl_idname = "VIEW3D_MT_toon_palette_group"
    bl_label = "Group Specials"

    @override
    def draw(self, context: Context):
        layout = self.layout

        layout.operator(
            VIEW3D_OT_toon_palette_add_group.bl_idname, text="Add Group", icon="ADD"
        )
        layout.operator(
            VIEW3D_OT_toon_palette_remove_group.bl_idname,
            text="Remove Group",
            icon="REMOVE",
        )
        layout.separator()
        layout.menu(VIEW3D_MT_toon_palette_merge_group.bl_idname, text="Merge Palette")
        layout.menu(
            VIEW3D_MT_toon_palette_merge_group_overwrite.bl_idname,
            text="Merge Palette (Overwrite)",
        )
