from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

from bpy.props import EnumProperty

from toon.manager import PaletteManager
from toon.props import Palette

from .base import PaletteOperator


class VIEW3D_OT_toon_palette_move(PaletteOperator):
    bl_idname = 'view3d.toon_move_palette'
    bl_label = 'Move Palette'
    bl_description = 'Move the selected palette'
    bl_options = {'REGISTER', 'UNDO'}

    direction_types = [
        ('UP', 'Up', ''),
        ('DOWN', 'Down', '')
    ]

    direction: EnumProperty(
        items=direction_types, options={'HIDDEN'}
    )

    @override
    def execute_operator(self, palette: Palette) -> set[OperatorReturnItems]:
        manager = PaletteManager.instance()
        i = manager.find(palette)
        offset = -1 if self.direction == 'UP' else 1

        if i + offset >= 0:
            manager.move(i, i + offset)

        return {'FINISHED'}


class VIEW3D_OT_toon_palette_move_slot(PaletteOperator):
    bl_idname = 'view3d.toon_move_up_palette'
    bl_label = 'Move Palette Slot'
    bl_description = 'Move the selected group or entry'
    bl_options = {'REGISTER', 'UNDO'}

    direction_types = [
        ('UP', 'Up', ''),
        ('DOWN', 'Down', '')
    ]

    direction: EnumProperty(
        items=direction_types, options={'HIDDEN'}
    )

    @classmethod
    @override
    def poll_operator(cls, palette: Palette) -> bool:
        return palette.id_data.library is None

    @override
    def execute_operator(self, palette: Palette) -> set[OperatorReturnItems]:
        pointer = palette.active_pointer()
        offset = -1 if self.direction == 'UP' else 1

        if pointer is None:
            return {'FINISHED'}
        elif pointer.entry is None and pointer.group_id + offset >= 0:
            last_slot_id = palette.active_slot_id
            result = palette.move(pointer.group_id, pointer.group_id + offset)

            if result:
                palette.update_slots()

                offset_size = len(palette.entries[pointer.group_id].entries) + 1
                palette.active_slot_id = last_slot_id + offset_size * offset
        elif pointer.entry_id + offset >= 0:
            result = pointer.group.move(pointer.entry_id, pointer.entry_id + offset)

            if result:
                palette.update_slots()

                palette.active_slot_id += offset

        return {'FINISHED'}
