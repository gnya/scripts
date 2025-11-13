from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

from bpy.types import Context, Operator

from .palette import Palette, PaletteManager


class VIEW3D_OT_toon_add_palette(Operator):
    bl_idname = 'view3d.toon_add_palette'
    bl_label = 'Add Palette'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        manager = PaletteManager.instance()
        manager.add('PALETTE')

        return {'FINISHED'}


class VIEW3D_OT_toon_remove_palette(Operator):
    bl_idname = 'view3d.toon_remove_palette'
    bl_label = 'Remove Palette'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        manager = PaletteManager.instance()
        manager.remove(context.palette)

        return {'FINISHED'}


class VIEW3D_OT_toon_add_palette_group(Operator):
    bl_idname = 'view3d.toon_add_palette_group'
    bl_label = 'Add Palette Group'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        palette: Palette = context.palette
        p = palette.active_pointer()

        if p is None:
            palette.add('Group')
            palette.update_slots()

            palette.active_slot_id = 0
        else:
            palette.add(p.group.name)
            palette.move(-1, p.group_id + 1)
            palette.update_slots()

            palette.active_slot_id += len(p.group.entries) - p.entry_id

        return {'FINISHED'}


class VIEW3D_OT_toon_remove_palette_group(Operator):
    bl_idname = 'view3d.toon_remove_palette_group'
    bl_label = 'Remove Palette Group'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        palette: Palette = context.palette
        p = palette.active_pointer()

        if p is not None and p.entry is None:
            palette.remove(p.group_id)
            palette.update_slots()

            if palette.active_slot_id >= len(palette.slots):
                palette.active_slot_id -= 1

        return {'FINISHED'}


class VIEW3D_OT_toon_add_palette_entry(Operator):
    bl_idname = 'view3d.toon_add_palette_entry'
    bl_label = 'Add Palette Entry'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        palette: Palette = context.palette
        p = palette.active_pointer()

        if p is None:
            return {'FINISHED'}
        elif p.entry is None:
            entry = p.group.add('Entry')
            entry.color = (1.0, 1.0, 1.0, 1.0)
            palette.update_slots()

            palette.active_slot_id += len(p.group.entries)
            p.group.show_expanded = True
        else:
            entry = p.group.add(p.entry.name)
            entry.color = p.entry.color
            p.group.move(-1, p.entry_id + 1)
            palette.update_slots()

            palette.active_slot_id += 1

        return {'FINISHED'}


class VIEW3D_OT_toon_remove_palette_entry(Operator):
    bl_idname = 'view3d.toon_remove_palette_entry'
    bl_label = 'Remove Palette Entry'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        palette: Palette = context.palette
        p = palette.active_pointer()

        if p is not None and p.entry is not None:
            p.group.remove(p.entry_id)
            palette.update_slots()

            if p.entry_id >= len(p.group.entries):
                palette.active_slot_id -= 1

        return {'FINISHED'}
