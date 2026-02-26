from typing import Any
from toon.utils import override

from bpy.props import StringProperty
from bpy.types import Context, UILayout, UIList

from toon.props import ToonPaletteUIItem
from toon.props import ToonPaletteUIPaletteState


class VIEW3D_UL_toon_palette_entry(UIList):
    bl_idname = 'VIEW3D_UL_toon_palette_entry'

    filter_name: StringProperty(
        name='Filter by Name', default='', options={'TEXTEDIT_UPDATE'}
    )

    @override
    def draw_item(
        self, context: Context, layout: UILayout, data: ToonPaletteUIPaletteState | None,
        item: ToonPaletteUIItem | None, icon: int | None, active_data: Any,
        active_property: str | None, index: int | None = 0, flt_flag: int | None = 0
    ):
        if data is None or item is None:
            return

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)

            if item.type == 'GROUP':
                i = 'DOWNARROW_HLT' if item.show_expanded else 'RIGHTARROW'
                row.prop(item, 'show_expanded', text='', emboss=False, icon=i)
                row.prop(item, 'group_name', text='', emboss=False)
            elif item.type == 'COLOR':
                row.separator(factor=3.0)
                # TODO Implement later.
                # row.row().prop(item, 'color', text='')
                row.prop(item, 'color_name', text='', emboss=False)
        elif self.layout_type in {'GRID'}:
            pass

    def _filter_name(self, name: str, filter_name: str):
        if not self.use_filter_invert:
            return filter_name.lower() in name.lower()
        else:
            return filter_name.lower() not in name.lower()

    def _filter_item(self, item: ToonPaletteUIItem) -> bool:
        if item.type == 'GROUP':
            if not self.filter_name:
                return True

            if self._filter_name(item.group_name, self.filter_name):
                return True

            for color in item.colors_data():
                if self._filter_name(color.name, self.filter_name):
                    return True
        elif item.type == 'COLOR':
            if not self.filter_name:
                return item.show_expanded

            if self._filter_name(item.color_name, self.filter_name):
                return item.show_expanded

        return False

    @override
    def filter_items(
        self, context: Context, data: ToonPaletteUIPaletteState | None, property: str
    ) -> tuple[list[int], list[int]]:
        if data is None:
            return [], []

        items = data.list_items
        filter_flags = [self.bitflag_filter_item] * len(items)

        for i, item in enumerate(items):
            flag = self._filter_item(item)

            if not (flag ^ self.use_filter_invert):
                filter_flags[i] = ~self.bitflag_filter_item

        return filter_flags, []
