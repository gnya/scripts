from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

import bpy
import json

from bpy.props import StringProperty
from bpy.types import Context, NodeSocketInterfaceColor, NodeTree, Operator
from json.decoder import JSONDecodeError

from toon.json import decode_palette, encode_node_tree, PaletteEncodeError
from toon.manager import PaletteManager


class VIEW3D_OT_toon_palette_add_by_node_tree(Operator):
    bl_idname = 'view3d.toon_add_palette_by_node_tree'
    bl_label = 'Convert NodeTree to Palette'
    bl_description = 'Convert the node tree to a palette'
    bl_options = {'REGISTER', 'UNDO'}

    id_name: StringProperty(name='Node Tree Name')

    id_lib: StringProperty(name='Node Tree Library Filepath', default='')

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        if not self.id_lib:
            id_key = self.id_name
        else:
            id_key = self.id_name, self.id_lib

        if id_key not in bpy.data.node_groups:
            self.report({'ERROR'}, f'Required node tree is missing. : {id_key}')

            return {'CANCELLED'}

        try:
            node_tree = bpy.data.node_groups[id_key]
            data = encode_node_tree(node_tree)
        except PaletteEncodeError as e:
            self.report({'ERROR'}, f'Failed to convert node tree. : {e.msg}')

            return {'CANCELLED'}
        else:
            manager = PaletteManager.instance()
            palette = manager.add(node_tree.name)
            decode_palette(data, palette)
            palette.update_slots()

        return {'FINISHED'}

    @staticmethod
    def poll_node_tree(node_tree: NodeTree):
        if node_tree.name.startswith('.'):
            return False
        elif len(node_tree.outputs) == 0:
            return False

        for o in node_tree.outputs:
            if not isinstance(o, NodeSocketInterfaceColor):
                return False

        return True


class VIEW3D_OT_toon_palette_add_by_clipboard(Operator):
    bl_idname = 'view3d.toon_add_palette_by_clipboard'
    bl_label = 'Convert Clipboard Text to Palette'
    bl_description = 'Convert json text on clipboard to a palette'
    bl_options = {'REGISTER', 'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        try:
            data = json.loads(bpy.context.window_manager.clipboard)
        except JSONDecodeError as e:
            self.report({'ERROR'}, f'Failed to decode json text. : {e.msg}')

            return {'CANCELLED'}
        else:
            manager = PaletteManager.instance()
            palette = manager.add('Palette')
            decode_palette(data, palette)
            palette.update_slots()

        return {'FINISHED'}
