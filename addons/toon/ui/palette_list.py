from typing import Any
from toon.utils import override

from bpy.props import StringProperty
from bpy.types import Context, UILayout, UIList

from toon.props import Palette, PalettePointer, PaletteSlot


class VIEW3D_UL_toon_palette_entry(UIList):
    bl_idname = 'VIEW3D_UL_toon_palette_entry'

    filter_name: StringProperty(
        name='Filter by Name', default='', options={'TEXTEDIT_UPDATE'}
    )

    @override
    def draw_item(
            self, context: Context, layout: UILayout, data: Palette | None,
            item: PaletteSlot | None, icon: int | None, active_data: Any,
            active_property: str | None, index: int | None = 0, flt_flag: int | None = 0
    ):
        if data is None or item is None:
            return

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            pointer = data.get_pointer(item)
            row = layout.row(align=True)

            if pointer is None:
                return
            elif pointer.entry is None:
                i = 'DOWNARROW_HLT' if pointer.group.show_expanded else 'RIGHTARROW'
                row.prop(pointer.group, 'show_expanded', text='', emboss=False, icon=i)
                row.prop(pointer.group, 'name', text='', emboss=False)
            else:
                row.separator(factor=3.0)

                if pointer.entry.type == 'COLOR':
                    row.row().prop(pointer.entry, 'color', text='')
                elif pointer.entry.type == 'TEXTURE':
                    row.row().prop(pointer.entry.node(), 'image', text='')
                elif pointer.entry.type == 'MIX':
                    row.row().prop(pointer.entry, 'mix_factor', text='', slider=True)

                row.prop(pointer.entry, 'name', text='', emboss=False)
        elif self.layout_type in {'GRID'}:
            pass

    def _filter_name(self, name: str, filter_name: str):
        if not self.use_filter_invert:
            return filter_name.lower() in name.lower()
        else:
            return filter_name.lower() not in name.lower()

    def _filter_item(self, pointer: PalettePointer | None) -> bool:
        if pointer is None:
            return False
        elif pointer.entry is not None:
            if not self.filter_name:
                return pointer.group.show_expanded

            if self._filter_name(pointer.entry.name, self.filter_name):
                return pointer.group.show_expanded
        else:
            if not self.filter_name:
                return True

            if self._filter_name(pointer.group.name, self.filter_name):
                return True

            for child in pointer.group.entries:
                if self._filter_name(child.name, self.filter_name):
                    return True

        return False

    @override
    def filter_items(
            self, context: Context, data: Palette | None, property: str
    ) -> tuple[list[int], list[int]]:
        if data is None:
            return [], []

        slots = getattr(data, property)
        filter_flags = [self.bitflag_filter_item] * len(slots)

        for i, slot in enumerate(slots):
            flag = self._filter_item(data.get_pointer(slot))

            if not (flag ^ self.use_filter_invert):
                filter_flags[i] = ~self.bitflag_filter_item

        return filter_flags, []
