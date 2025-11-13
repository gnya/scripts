from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

from bpy.props import EnumProperty
from bpy.types import Context, Operator

from .palette import Palette


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
        p = palette.active_entry()
        offset = -1 if self.direction == 'UP' else 1

        if p is None:
            return {'FINISHED'}
        elif p.entry is None and p.group_id + offset >= 0:
            last_slot_id = palette.active_slot_id
            result = palette.move(p.group_id, p.group_id + offset)

            if result:
                palette.update_slots()

                offset_size = len(palette.entries[p.group_id].entries) + 1
                palette.active_slot_id = last_slot_id + offset_size * offset
        elif p.entry_id + offset >= 0:
            result = p.group.move(p.entry_id, p.entry_id + offset)

            if result:
                palette.update_slots()

                palette.active_slot_id += offset

        return {'FINISHED'}
