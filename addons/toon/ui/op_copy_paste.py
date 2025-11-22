from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

import bpy
import json

from json.decoder import JSONDecodeError

from toon.json import decode_palette, encode_palette
from toon.props import Palette

from .op_base import PaletteOperator


class VIEW3D_OT_toon_copy_palette(PaletteOperator):
    bl_idname = 'view3d.toon_copy_palette'
    bl_label = 'Copy Palette'
    bl_description = 'Copy the selected palette to clipboard as json'
    bl_options = {'REGISTER', 'UNDO'}

    @override
    def execute_operator(self, palette: Palette) -> set[OperatorReturnItems]:
        data = encode_palette(palette)
        bpy.context.window_manager.clipboard = json.dumps(data)

        return {'FINISHED'}


class VIEW3D_OT_toon_paste_palette(PaletteOperator):
    bl_idname = 'view3d.toon_paste_palette'
    bl_label = 'Paste Palette'
    bl_description = 'Paste json text on clipboard to the selected palette'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    @override
    def poll_operator(cls, palette: Palette) -> bool:
        return palette.id_data.library is None

    @override
    def execute_operator(self, palette: Palette) -> set[OperatorReturnItems]:
        try:
            data = json.loads(bpy.context.window_manager.clipboard)
        except JSONDecodeError:
            return {'CANCELLED'}
        else:
            decode_palette(data, palette)
            palette.update_slots()

        return {'FINISHED'}
