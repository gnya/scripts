from bpy.props import EnumProperty
from bpy.types import Context, Operator
from typing import TYPE_CHECKING

from toon.utils import override

from .props import PaletteUI

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
        p = palette.active_item()

        if p is None:
            palette.add('Group')
            palette.update_slots()

            palette.active_slot_id = 0
        else:
            palette.add(p.group.name)
            palette.move(-1, p.group_id + 1)
            palette.update_slots()

            palette.active_slot_id += len(p.group.items) - p.item_id

        return {'FINISHED'}


class VIEW3D_OT_toon_remove_palette_group(Operator):
    bl_idname = 'view3d.toon_remove_palette_group'
    bl_label = 'Remove Group'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set['OperatorReturnItems']:
        palette: PaletteUI = context.palette
        p = palette.active_item()

        if p is not None and p.item is None:
            palette.remove(p.group_id)
            palette.update_slots()

            if palette.active_slot_id >= len(palette.slots):
                palette.active_slot_id -= 1

        return {'FINISHED'}


class VIEW3D_OT_toon_add_palette_item(Operator):
    bl_idname = 'view3d.toon_add_palette_item'
    bl_label = 'Add Item'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set['OperatorReturnItems']:
        palette: PaletteUI = context.palette
        p = palette.active_item()

        if p is None:
            return {'FINISHED'}
        elif p.item is None:
            item = p.group.add('Item')
            item.color = (1.0, 1.0, 1.0, 1.0)
            palette.update_slots()

            palette.active_slot_id += len(p.group.items)
            p.group.show_expanded = True
        else:
            item = p.group.add(p.item.name)
            item.color = p.item.color
            p.group.move(-1, p.item_id + 1)
            palette.update_slots()

            palette.active_slot_id += 1

        return {'FINISHED'}


class VIEW3D_OT_toon_remove_palette_item(Operator):
    bl_idname = 'view3d.toon_remove_palette_item'
    bl_label = 'Remove Item'
    bl_options = {'UNDO'}

    @override
    def execute(self, context: Context) -> set['OperatorReturnItems']:
        palette: PaletteUI = context.palette
        p = palette.active_item()

        if p is not None and p.item is not None:
            p.group.remove(p.item_id)
            palette.update_slots()

            if p.item_id >= len(p.group.items):
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
        p = palette.active_item()
        offset = -1 if self.direction == 'UP' else 1

        if p is None:
            return {'FINISHED'}
        elif p.item is None:
            if p.group_id + offset < 0:
                return {'FINISHED'}

            result = palette.move(p.group_id, p.group_id + offset)

            if result:
                palette.update_slots()

                o = len(palette.items[p.group_id].items) + 1
                palette.active_slot_id += o * offset
        else:
            if p.item_id + offset < 0:
                return {'FINISHED'}

            result = p.group.move(p.item_id, p.item_id + offset)

            if result:
                palette.update_slots()

                palette.active_slot_id += offset

        return {'FINISHED'}
