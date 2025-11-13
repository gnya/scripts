from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

from bpy.props import PointerProperty
from bpy.types import (
    Context, Event, NodeSocketInterfaceColor, NodeTree, Operator, WindowManager
)

from .palette import PaletteManager


class VIEW3D_OT_toon_convert_palette(Operator):
    bl_idname = 'view3d.toon_convert_palette'
    bl_label = 'Convert NodeTree to Palette'
    bl_options = {'UNDO'}

    PROP_NAME = 'toon_temp_selected_node_tree'

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        node_tree = getattr(
            context.window_manager,
            VIEW3D_OT_toon_convert_palette.PROP_NAME,
            None
        )

        if node_tree is None:
            return {'CANCELLED'}

        manager = PaletteManager.instance()
        palette = manager.add(node_tree.name)

        outputs = node_tree.outputs
        output_node = node_tree.nodes.get('Group Output')

        if output_node is not None:
            outputs = output_node.inputs

        palette_data = {palette.name: []}

        for i in range(len(node_tree.outputs)):
            name = outputs[i].name.split('|', 1)
            group_name = name[0].strip() if len(name) > 1 else palette.name
            entry_name = name[-1].strip()

            if group_name not in palette_data:
                palette_data[group_name] = []

            palette_data[group_name].append((i, entry_name))

        for group_name, entries in palette_data.items():
            if len(entries) == 0:
                continue

            group = palette.add(group_name)

            for i, entry_name in entries:
                entry = group.add(entry_name)
                entry.color = outputs[i].default_value

        palette.update_slots()

        return {'FINISHED'}

    @override
    def invoke(self, context: Context, event: Event) -> set[OperatorReturnItems]:
        return context.window_manager.invoke_props_dialog(self)

    @override
    def draw(self, context: Context):
        layout = self.layout

        layout.activate_init = True
        layout.prop(
            context.window_manager,
            VIEW3D_OT_toon_convert_palette.PROP_NAME,
            text=''
        )

    @staticmethod
    def register():
        def _poll_node_tree(self: WindowManager, node_tree: NodeTree):
            if node_tree.name.startswith('.'):
                return False
            elif len(node_tree.outputs) == 0:
                return False

            for o in node_tree.outputs:
                if not isinstance(o, NodeSocketInterfaceColor):
                    return False

            return True

        setattr(
            WindowManager,
            VIEW3D_OT_toon_convert_palette.PROP_NAME,
            PointerProperty(type=NodeTree, poll=_poll_node_tree)
        )

    @staticmethod
    def unregister():
        delattr(
            WindowManager,
            VIEW3D_OT_toon_convert_palette.PROP_NAME,
        )
