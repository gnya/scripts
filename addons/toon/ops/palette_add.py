from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

from bpy.types import Context, Operator

from toon.props import ToonPaletteFacade


class VIEW3D_OT_toon_palette_add(Operator):
    bl_idname = 'view3d.toon_add_palette'
    bl_label = 'Add Palette'
    bl_description = 'Add a empty palette'
    bl_options = {'REGISTER', 'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        facade = ToonPaletteFacade.instance()
        facade.add('Palette')

        return {'FINISHED'}
