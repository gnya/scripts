from __future__ import annotations

import json
from json.decoder import JSONDecodeError
from typing import TYPE_CHECKING

import bpy
from bpy.props import EnumProperty
from bpy.types import Operator

from toon.palette import PaletteDecodeError, decode_palette, encode_palette, get_facade
from toon.props import ToonPaletteSearchIndex, ToonPaletteUIState
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems
    from bpy.types import Context

    from toon.props import ToonPaletteUIPaletteState


class ToonPaletteOperator(Operator):
    @classmethod
    def _poll_impl(cls, state: ToonPaletteUIPaletteState) -> bool:
        return True

    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        raise NotImplementedError()

    @classmethod
    @override
    def poll(cls, context: Context) -> bool:
        if not hasattr(context, "palette_state"):
            return False

        return cls._poll_impl(context.palette_state)

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
    bl_description = "Add empty palette"
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
    bl_description = "Remove active palette"
    bl_options = {"REGISTER", "UNDO"}

    @override
    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        return get_facade().remove(state.palette_name)


class VIEW3D_OT_toon_palette_add_group(ToonPaletteOperator):
    bl_idname = "view3d.toon_palette_add_group"
    bl_label = "Add Palette Group"
    bl_description = "Add empty group to active palette"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    @override
    def _poll_impl(cls, state: ToonPaletteUIPaletteState) -> bool:
        return not (state.is_orphans() or state.is_linked())

    @override
    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        palette = state.palette_data()

        if palette is None or palette.is_orphens:
            return False
        elif not palette.add("Group"):
            return False

        state.active_index = len(state.list_items)

        return True


class VIEW3D_OT_toon_palette_remove_group(ToonPaletteOperator):
    bl_idname = "view3d.toon_palette_remove_group"
    bl_label = "Remove Palette Group"
    bl_description = "Remove avtive group from palette"
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
    bl_description = "Add color to active palette"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    @override
    def _poll_impl(cls, state: ToonPaletteUIPaletteState) -> bool:
        return not state.is_linked()

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
    bl_description = "Remove active color from palette"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    @override
    def _poll_impl(cls, state: ToonPaletteUIPaletteState) -> bool:
        return not state.is_linked()

    @override
    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        item = state.active_item()

        if item is None or item.type != "COLOR":
            return False

        group = item.group_data()

        if group is None:
            return False
        elif not group.remove(item.color_name):
            return False

        max_index = item.header_index + len(list(group.colors()))
        state.active_index = min(state.active_index, max_index)

        return True


class VIEW3D_OT_toon_palette_merge(ToonPaletteOperator):
    bl_idname = "view3d.toon_palette_merge"
    bl_label = "Merge Palette"
    bl_description = "Merge active palette to selected"
    bl_options = {"REGISTER", "UNDO"}

    @override
    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        return True


class VIEW3D_OT_toon_palette_merge_group(ToonPaletteOperator):
    bl_idname = "view3d.toon_palette_merge_group"
    bl_label = "Merge Group"
    bl_description = "Merge active group to selected"
    bl_options = {"REGISTER", "UNDO"}

    @override
    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        return True


class VIEW3D_OT_toon_palette_copy(ToonPaletteOperator):
    bl_idname = "view3d.toon_palette_copy"
    bl_label = "Copy Palette"
    bl_description = "Copy palette to clipboard as JSON"
    bl_options = {"REGISTER", "UNDO"}

    @override
    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        palette = state.palette_data()

        if palette is None:
            return False

        bpy.context.window_manager.clipboard = json.dumps(encode_palette(palette))

        return True


class VIEW3D_OT_toon_palette_paste(Operator):
    bl_idname = "view3d.toon_palette_paste"
    bl_label = "Paste Palette"
    bl_description = "Paste JSON from clipboard as palette"
    bl_options = {"REGISTER", "UNDO"}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        try:
            data = json.loads(bpy.context.window_manager.clipboard)
            decode_palette(data, get_facade())
        except JSONDecodeError as e:
            self.report({"ERROR"}, f"Failed to decode json text. : {e.msg}")

            return {"CANCELLED"}
        except PaletteDecodeError as e:
            self.report({"ERROR"}, f"Failed to decode palette data. : {e}")

            return {"CANCELLED"}
        else:
            ToonPaletteUIState.request_update()
            ToonPaletteSearchIndex.request_update()

            return {"FINISHED"}


class VIEW3D_OT_toon_palette_move(ToonPaletteOperator):
    bl_idname = "view3d.toon_palette_move"
    bl_label = "Move Palette"
    bl_description = "Move active palette"
    bl_options = {"REGISTER", "UNDO"}

    direction_types = [("UP", "Up", ""), ("DOWN", "Down", "")]

    direction: EnumProperty(items=direction_types, options={"HIDDEN"})

    @classmethod
    @override
    def _poll_impl(cls, state: ToonPaletteUIPaletteState) -> bool:
        return not state.is_orphans()

    @override
    def _execute_impl(self, state: ToonPaletteUIPaletteState) -> bool:
        offset = -1 if self.direction == "UP" else 1
        index = state.palette_index

        get_facade().move(index, index + offset)

        return True


class VIEW3D_OT_toon_palette_move_item(ToonPaletteOperator):
    bl_idname = "view3d.toon_palette_move_item"
    bl_label = "Move Palette Item"
    bl_description = "Move active group or color"
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
        elif item.type == "COLOR" and not item.is_linked():
            group = item.group_data()

            if group is None:
                return False

            index = item.color_index

            if group.move(index, index + offset):
                state.active_index += offset

            return True

        return False
