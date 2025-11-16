from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

from bpy.types import Context, Operator


class VIEW3D_OT_toon_copy_palette(Operator):
    bl_idname = 'view3d.toon_copy_palette'
    bl_label = 'Copy Palette'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        return {'FINISHED'}


class VIEW3D_OT_toon_paste_palette(Operator):
    bl_idname = 'view3d.toon_paste_palette'
    bl_label = 'Paste Palette'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        return {'FINISHED'}
