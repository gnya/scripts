from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

from bpy.types import Context, Operator

from toon.props import Palette


class PaletteOperator(Operator):
    @classmethod
    def poll_operator(cls, palette: Palette) -> bool:
        return True

    def execute_operator(self, palette: Palette) -> set[OperatorReturnItems]:
        raise NotImplementedError()

    @classmethod
    @override
    def poll(cls, context: Context) -> bool:
        if not hasattr(context, 'palette'):
            return False

        return cls.poll_operator(context.palette)

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        if not hasattr(context, 'palette'):
            return {'FINISHED'}

        return self.execute_operator(context.palette)
