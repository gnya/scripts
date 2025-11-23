from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

from bpy.types import Context, Operator

from toon.manager import PaletteManager
from toon.props import Palette

from .op_base import PaletteOperator


def _add_group(palette: Palette):
    pointer = palette.active_pointer()
    name, group_id, slot_id = 'Group', -1, 0

    if pointer is not None:
        name = pointer.group.name
        group_id = pointer.group_id + 1
        offset_slot_id = len(pointer.group.entries) - pointer.entry_id
        slot_id = palette.active_slot_id + offset_slot_id

    palette.add(name)
    palette.move(-1, group_id)
    palette.update_slots()

    palette.active_slot_id = slot_id


def _add_entry(palette: Palette):
    pointer = palette.active_pointer()

    if pointer is None:
        return

    name = 'Entry'
    color = (1.0, 1.0, 1.0, 1.0)
    entry_id = -1
    offset_slot_id = len(pointer.group.entries) + 1

    if pointer.entry is not None:
        name = pointer.entry.name
        color = pointer.entry.color
        entry_id = pointer.entry_id + 1
        offset_slot_id = 1

    entry = pointer.group.add(name)
    entry.color = color
    pointer.group.move(-1, entry_id)
    palette.update_slots()

    palette.active_slot_id += offset_slot_id
    pointer.group.show_expanded = True


class VIEW3D_OT_toon_add_palette(Operator):
    bl_idname = 'view3d.toon_add_palette'
    bl_label = 'Add Palette'
    bl_description = 'Add a empty palette'
    bl_options = {'REGISTER', 'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        manager = PaletteManager.instance()
        manager.add('Palette')

        return {'FINISHED'}


class VIEW3D_OT_toon_add_palette_group(PaletteOperator):
    bl_idname = 'view3d.toon_add_palette_group'
    bl_label = 'Add Palette Group'
    bl_description = 'Add a empty group to the selected palette'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    @override
    def poll_operator(cls, palette: Palette) -> bool:
        return palette.id_data.library is None

    @override
    def execute_operator(self, palette: Palette) -> set[OperatorReturnItems]:
        _add_group(palette)

        return {'FINISHED'}


class VIEW3D_OT_toon_add_palette_entry(PaletteOperator):
    bl_idname = 'view3d.toon_add_palette_entry'
    bl_label = 'Add Palette Entry'
    bl_description = 'Add a entry to the selected palette'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    @override
    def poll_operator(cls, palette: Palette) -> bool:
        return palette.id_data.library is None

    @override
    def execute_operator(self, palette: Palette) -> set[OperatorReturnItems]:
        if len(palette.entries) == 0:
            _add_group(palette)

        _add_entry(palette)

        return {'FINISHED'}
