from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

from bpy.props import EnumProperty
from bpy.types import Context, Operator

from toon.manager import PaletteManager
from toon.props import Palette


class VIEW3D_OT_toon_move_palette(Operator):
    bl_idname = 'view3d.toon_move_palette'
    bl_label = 'Move Palette'
    bl_options = {'UNDO'}

    direction_types = [
        ('UP', 'Up', ''),
        ('DOWN', 'Down', '')
    ]

    direction: EnumProperty(items=direction_types)

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        palette: Palette = context.palette
        manager = PaletteManager.instance()
        i = manager.find(palette)
        offset = -1 if self.direction == 'UP' else 1

        if i + offset >= 0:
            manager.move(i, i + offset)

        return {'FINISHED'}


class VIEW3D_OT_toon_move_palette_slot(Operator):
    bl_idname = 'view3d.toon_move_up_palette'
    bl_label = 'Move Palette Slot'
    bl_options = {'UNDO'}

    direction_types = [
        ('UP', 'Up', ''),
        ('DOWN', 'Down', '')
    ]

    direction: EnumProperty(items=direction_types)

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        palette: Palette = context.palette
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
