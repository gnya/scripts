from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

import json

from bpy.types import Context, Operator
from json.decoder import JSONDecodeError

from toon.json import decode_palette, encode_palette
from toon.props import Palette


class VIEW3D_OT_toon_copy_palette(Operator):
    bl_idname = 'view3d.toon_copy_palette'
    bl_label = 'Copy Palette'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        palette: Palette = context.palette
        data = encode_palette(palette)
        context.window_manager.clipboard = json.dumps(data)

        return {'FINISHED'}


class VIEW3D_OT_toon_paste_palette(Operator):
    bl_idname = 'view3d.toon_paste_palette'
    bl_label = 'Paste Palette'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        palette: Palette = context.palette

        try:
            data = json.loads(context.window_manager.clipboard)
        except JSONDecodeError:
            return {'CANCELLED'}
        else:
            decode_palette(data, palette)
            palette.update_slots()

        return {'FINISHED'}
