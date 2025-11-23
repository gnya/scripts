from toon.utils import override

import bpy

from bpy.types import Context, Menu

from toon.ops import VIEW3D_OT_toon_add_palette
from toon.ops import VIEW3D_OT_toon_add_palette_group
from toon.ops import VIEW3D_OT_toon_add_palette_by_node_tree
from toon.ops import VIEW3D_OT_toon_add_palette_by_clipboard
from toon.ops import VIEW3D_OT_toon_remove_palette_group
from toon.ops import VIEW3D_OT_toon_copy_palette
from toon.ops import VIEW3D_OT_toon_paste_palette
from toon.ops import VIEW3D_OT_toon_move_palette


class VIEW3D_MT_toon_palette_add_menu(Menu):
    bl_idname = 'VIEW3D_MT_toon_palette_add_menu'
    bl_label = 'Add Palette'

    @override
    def draw(self, context: Context):
        layout = self.layout

        layout.operator(
            VIEW3D_OT_toon_add_palette.bl_idname,
            text='Add Empty Palette', icon='ADD'
        )
        layout.operator(
            VIEW3D_OT_toon_add_palette_by_clipboard.bl_idname,
            text='From Clipboard', icon='PASTEDOWN'
        )
        layout.separator()

        operator_type = VIEW3D_OT_toon_add_palette_by_node_tree

        for node_tree in bpy.data.node_groups:
            if not operator_type.poll_node_tree(node_tree):
                continue

            o = layout.operator(
                operator_type.bl_idname,
                text=f'From {node_tree.name}', icon='NODETREE'
            )
            o.id_name = node_tree.name

            if node_tree.library is not None:
                o.id_lib = node_tree.library.filepath


class VIEW3D_MT_toon_palette_menu(Menu):
    bl_idname = 'VIEW3D_MT_toon_palette_menu'
    bl_label = 'Palette Specials'

    @override
    def draw(self, context: Context):
        layout = self.layout

        layout.operator(
            VIEW3D_OT_toon_copy_palette.bl_idname,
            text='Copy Palette', icon='COPYDOWN'
        )
        layout.operator(
            VIEW3D_OT_toon_paste_palette.bl_idname,
            text='Paste Palette', icon='PASTEDOWN'
        )
        layout.separator()
        o = layout.operator(
            VIEW3D_OT_toon_move_palette.bl_idname,
            text='Move Palette', icon='TRIA_UP'
        )
        o.direction = 'UP'
        o = layout.operator(
            VIEW3D_OT_toon_move_palette.bl_idname,
            text='Move Palette', icon='TRIA_DOWN'
        )
        o.direction = 'DOWN'


class VIEW3D_MT_toon_palette_group_menu(Menu):
    bl_idname = 'VIEW3D_MT_toon_palette_group_menu'
    bl_label = 'Group Specials'

    @override
    def draw(self, context: Context):
        layout = self.layout

        layout.operator(
            VIEW3D_OT_toon_add_palette_group.bl_idname,
            text='Add Group', icon='ADD'
        )
        layout.operator(
            VIEW3D_OT_toon_remove_palette_group.bl_idname,
            text='Remove Group', icon='REMOVE'
        )
