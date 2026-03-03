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
from toon.utils import override

if TYPE_CHECKING:
    from bpy.types import Context


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

        # for node_tree in bpy.data.node_groups:
        #     if not poll_node_tree(node_tree):
        #         continue

        #     o = layout.operator(
        #         VIEW3D_OT_toon_palette_add_by_node_tree.bl_idname,
        #         text=f"From {node_tree.name}",
        #         icon="NODETREE",
        #     )
        #     o.id_name = node_tree.name

        #     if node_tree.library is not None:
        #         o.id_lib = node_tree.library.filepath


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
        layout.operator(VIEW3D_OT_toon_palette_merge.bl_idname, text="Merge Palette")
        layout.separator()
        o = layout.operator(
            VIEW3D_OT_toon_palette_move.bl_idname, text="Move Palette", icon="TRIA_UP"
        )
        o.direction = "UP"
        o = layout.operator(
            VIEW3D_OT_toon_palette_move.bl_idname, text="Move Palette", icon="TRIA_DOWN"
        )
        o.direction = "DOWN"


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
        layout.operator(
            VIEW3D_OT_toon_palette_merge_group.bl_idname, text="Merge Group"
        )
