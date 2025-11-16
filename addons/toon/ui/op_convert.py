from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

from bpy.props import PointerProperty
from bpy.types import (
    Context, Event, NodeSocketInterfaceColor, NodeTree, Operator, WindowManager
)

from toon.json import decode_palette, encode_node_tree
from toon.manager import PaletteManager


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
            return {'FINISHED'}

        manager = PaletteManager.instance()
        palette = manager.add(node_tree.name)
        data = encode_node_tree(node_tree)
        decode_palette(data, palette)
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
            VIEW3D_OT_toon_convert_palette.PROP_NAME
        )
