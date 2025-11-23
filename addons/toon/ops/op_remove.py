from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

from toon.manager import PaletteManager
from toon.props import Palette

from .op_base import PaletteOperator


def _remove_group(palette: Palette):
    pointer = palette.active_pointer()

    if pointer is None:
        return

    slot_id = -1

    if pointer.group_id > 0:
        previous_group = palette.entries[pointer.group_id - 1]
        offset_slot_id = len(previous_group.entries) + pointer.entry_id + 2
        slot_id = palette.active_slot_id - offset_slot_id

    palette.remove(pointer.group_id)
    palette.update_slots()

    palette.active_slot_id = slot_id


def _remove_entry(palette: Palette):
    pointer = palette.active_pointer()

    if pointer is None or pointer.entry is None:
        return

    offset_slot_id = 0

    if pointer.entry_id >= len(pointer.group.entries) - 1:
        offset_slot_id = -1

    pointer.group.remove(pointer.entry_id)
    palette.update_slots()

    palette.active_slot_id += offset_slot_id


class VIEW3D_OT_toon_remove_palette(PaletteOperator):
    bl_idname = 'view3d.toon_remove_palette'
    bl_label = 'Remove Palette'
    bl_description = 'Remove the selected palette'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    @override
    def poll_operator(cls, palette: Palette) -> bool:
        return palette.id_data.library is None

    @override
    def execute_operator(self, palette: Palette) -> set[OperatorReturnItems]:
        manager = PaletteManager.instance()
        manager.remove(palette)

        return {'FINISHED'}


class VIEW3D_OT_toon_remove_palette_group(PaletteOperator):
    bl_idname = 'view3d.toon_remove_palette_group'
    bl_label = 'Remove Palette Group'
    bl_description = 'Remove the selected group from the active palette'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    @override
    def poll_operator(cls, palette: Palette) -> bool:
        return palette.id_data.library is None

    @override
    def execute_operator(self, palette: Palette) -> set[OperatorReturnItems]:
        _remove_group(palette)

        return {'FINISHED'}


class VIEW3D_OT_toon_remove_palette_entry(PaletteOperator):
    bl_idname = 'view3d.toon_remove_palette_entry'
    bl_label = 'Remove Palette Entry'
    bl_description = 'Remove the selected entry from the active palette'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    @override
    def poll_operator(cls, palette: Palette) -> bool:
        return palette.id_data.library is None

    @override
    def execute_operator(self, palette: Palette) -> set[OperatorReturnItems]:
        _remove_entry(palette)

        return {'FINISHED'}
