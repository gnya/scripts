from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

from bpy.types import Context, Operator

from toon.manager import PaletteManager
from toon.props import Palette


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


class VIEW3D_OT_toon_add_palette(Operator):
    bl_idname = 'view3d.toon_add_palette'
    bl_label = 'Add Palette'
    bl_options = {'REGISTER', 'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        manager = PaletteManager.instance()
        manager.add('PALETTE')

        return {'FINISHED'}


class VIEW3D_OT_toon_remove_palette(Operator):
    bl_idname = 'view3d.toon_remove_palette'
    bl_label = 'Remove Palette'
    bl_options = {'REGISTER', 'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        manager = PaletteManager.instance()
        manager.remove(context.palette)

        return {'FINISHED'}


class VIEW3D_OT_toon_add_palette_group(Operator):
    bl_idname = 'view3d.toon_add_palette_group'
    bl_label = 'Add Palette Group'
    bl_options = {'REGISTER', 'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        _add_group(context.palette)

        return {'FINISHED'}


class VIEW3D_OT_toon_remove_palette_group(Operator):
    bl_idname = 'view3d.toon_remove_palette_group'
    bl_label = 'Remove Palette Group'
    bl_options = {'REGISTER', 'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        _remove_group(context.palette)

        return {'FINISHED'}


class VIEW3D_OT_toon_add_palette_entry(Operator):
    bl_idname = 'view3d.toon_add_palette_entry'
    bl_label = 'Add Palette Entry'
    bl_options = {'REGISTER', 'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        if len(context.palette.entries) == 0:
            _add_group(context.palette)

        _add_entry(context.palette)

        return {'FINISHED'}


class VIEW3D_OT_toon_remove_palette_entry(Operator):
    bl_idname = 'view3d.toon_remove_palette_entry'
    bl_label = 'Remove Palette Entry'
    bl_options = {'REGISTER', 'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        _remove_entry(context.palette)

        return {'FINISHED'}
