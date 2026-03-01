from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.props import EnumProperty
from bpy.types import Operator

from toon.palette import get_facade
from toon.props import ToonPaletteSearchIndex, ToonPaletteUIState
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems
    from bpy.types import Context

    from toon.props import ToonPaletteUIPaletteState


class ToonPaletteOperator(Operator):
    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        raise NotImplementedError()

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        if not hasattr(context, "palette_state"):
            return {"CANCELLED"}
        elif not self._execute_impl(context.palette_state):
            return {"CANCELLED"}

        ToonPaletteUIState.request_update()
        ToonPaletteSearchIndex.request_update()

        return {"FINISHED"}


class VIEW3D_OT_toon_palette_add(Operator):
    bl_idname = "view3d.toon_palette_add"
    bl_label = "Add Palette"
    bl_description = "Add a empty palette"
    bl_options = {"REGISTER", "UNDO"}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        if not get_facade().add("Palette"):
            return {"CANCELLED"}

        ToonPaletteUIState.request_update()
        ToonPaletteSearchIndex.request_update()

        return {"FINISHED"}


class VIEW3D_OT_toon_palette_remove(ToonPaletteOperator):
    bl_idname = "view3d.toon_palette_remove"
    bl_label = "Remove Palette"
    bl_description = "Remove the context palette"
    bl_options = {"REGISTER", "UNDO"}

    @override
    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        return get_facade().remove(state.palette_name)


class VIEW3D_OT_toon_palette_add_group(ToonPaletteOperator):
    bl_idname = "view3d.toon_palette_add_group"
    bl_label = "Add Palette Group"
    bl_description = "Add a empty group to the context palette"
    bl_options = {"REGISTER", "UNDO"}

    @override
    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        palette = state.palette_data()

        if palette is None:
            return False
        elif not palette.add("Group"):
            return False

        state.active_index = len(state.list_items)

        return True


class VIEW3D_OT_toon_palette_remove_group(ToonPaletteOperator):
    bl_idname = "view3d.toon_palette_remove_group"
    bl_label = "Remove Palette Group"
    bl_description = "Remove the context group from the context palette"
    bl_options = {"REGISTER", "UNDO"}

    @override
    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        palette = state.palette_data()
        item = state.active_item()

        if palette is None or item is None:
            return False
        elif not palette.remove(item.group_name):
            return False

        state.active_index = item.header_index

        return True


class VIEW3D_OT_toon_palette_add_color(ToonPaletteOperator):
    bl_idname = "view3d.toon_palette_add_color"
    bl_label = "Add Palette Color"
    bl_description = "Add a color to the context palette"
    bl_options = {"REGISTER", "UNDO"}

    @override
    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        item = state.active_item()

        if item is None:
            return False

        group = item.group_data()

        if group is None:
            return False
        elif not group.add("Color"):
            return False

        item.show_expanded = True
        state.active_index = item.header_index + len(list(group.colors()))

        return True


class VIEW3D_OT_toon_palette_remove_color(ToonPaletteOperator):
    bl_idname = "view3d.toon_palette_remove_color"
    bl_label = "Remove Palette Color"
    bl_description = "Remove the context color from the context palette"
    bl_options = {"REGISTER", "UNDO"}

    @override
    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        item = state.active_item()

        if item is None or item.type != "COLOR":
            return False

        group = item.group_data()

        if group is None:
            return False
        elif not group.remove(item.socket_index):
            return False

        max_index = item.header_index + len(list(group.colors()))
        state.active_index = min(state.active_index, max_index)

        return True


class VIEW3D_OT_toon_palette_move(ToonPaletteOperator):
    bl_idname = "view3d.toon_palette_move"
    bl_label = "Move Palette"
    bl_description = "Move the context palette"
    bl_options = {"REGISTER", "UNDO"}

    direction_types = [("UP", "Up", ""), ("DOWN", "Down", "")]

    direction: EnumProperty(items=direction_types, options={"HIDDEN"})

    @override
    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        offset = -1 if self.direction == "UP" else 1
        index = state.palette_index

        get_facade().move(index, index + offset)

        return True


class VIEW3D_OT_toon_palette_move_item(ToonPaletteOperator):
    bl_idname = "view3d.toon_palette_move_item"
    bl_label = "Move Palette Item"
    bl_description = "Move the context group or color"
    bl_options = {"REGISTER", "UNDO"}

    direction_types = [("UP", "Up", ""), ("DOWN", "Down", "")]

    direction: EnumProperty(items=direction_types, options={"HIDDEN"})

    @override
    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        item = state.active_item()

        if item is None:
            return False

        offset = -1 if self.direction == "UP" else 1

        if item.type == "GROUP":
            palette = item.palette_data()

            if palette is None:
                return False

            index = item.group_index
            dist = palette.dist(index, index + offset)

            if palette.move(index, index + offset):
                state.active_index += offset * dist

            return True
        elif item.type == "COLOR":
            group = item.group_data()

            if group is None:
                return False

            index = item.socket_index

            if group.move(index, index + offset):
                state.active_index += offset

            return True

        return False
