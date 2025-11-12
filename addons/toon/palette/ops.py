from bpy.props import EnumProperty
from bpy.types import Context, Operator
from typing import TYPE_CHECKING

from toon.utils import override

from .palette import PaletteUI

# Type check.
if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems


class VIEW3D_OT_toon_add_palette(Operator):
    bl_idname = 'view3d.toon_add_palette'
    bl_label = 'Add Palette'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set['OperatorReturnItems']:
        PaletteUI.new_instance('PALETTE')

        return {'FINISHED'}


class VIEW3D_OT_toon_remove_palette(Operator):
    bl_idname = 'view3d.toon_remove_palette'
    bl_label = 'Remove Palette'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set['OperatorReturnItems']:
        palette: PaletteUI = context.palette
        PaletteUI.del_instance(palette)

        return {'FINISHED'}


class VIEW3D_OT_toon_add_palette_group(Operator):
    bl_idname = 'view3d.toon_add_palette_group'
    bl_label = 'Add Group'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set['OperatorReturnItems']:
        palette: PaletteUI = context.palette
        p = palette.active_entry()

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
    bl_label = 'Remove Group'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set['OperatorReturnItems']:
        palette: PaletteUI = context.palette
        p = palette.active_entry()

        if p is not None and p.entry is None:
            palette.remove(p.group_id)
            palette.update_slots()

            if palette.active_slot_id >= len(palette.slots):
                palette.active_slot_id -= 1

        return {'FINISHED'}


class VIEW3D_OT_toon_add_palette_entry(Operator):
    bl_idname = 'view3d.toon_add_palette_entry'
    bl_label = 'Add Entry'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set['OperatorReturnItems']:
        palette: PaletteUI = context.palette
        p = palette.active_entry()

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
    bl_label = 'Remove Entry'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set['OperatorReturnItems']:
        palette: PaletteUI = context.palette
        p = palette.active_entry()

        if p is not None and p.entry is not None:
            p.group.remove(p.entry_id)
            palette.update_slots()

            if p.entry_id >= len(p.group.entries):
                palette.active_slot_id -= 1

        return {'FINISHED'}


class VIEW3D_OT_toon_move_palette_slot(Operator):
    bl_idname = 'view3d.toon_move_up_palette'
    bl_label = 'Move Up'
    bl_options = {'UNDO'}

    direction_types = [
        ('UP', 'Up', ''),
        ('DOWN', 'Down', '')
    ]

    direction: EnumProperty(items=direction_types)

    @override
    def execute(self, context: Context) -> set['OperatorReturnItems']:
        palette: PaletteUI = context.palette
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
