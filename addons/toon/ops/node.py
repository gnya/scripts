from __future__ import annotations
from typing import TYPE_CHECKING
from toon.utils import override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems

from bpy.types import Context, Operator

from toon.shaders import compile_all_shaders, register_shaders
from toon.utils import all_node_itr


class NODE_OT_toon_node_reload_all(Operator):
    bl_idname = 'node.toon_node_reload_all'
    bl_label = 'Reload All Nodes'
    bl_description = 'Reload all toon nodes'
    bl_options = {'REGISTER', 'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        for node in all_node_itr():
            if hasattr(node, 'reload'):
                node.reload()

        return {'FINISHED'}


class NODE_OT_toon_node_compile_all(Operator):
    bl_idname = 'node.toon_node_compile_all'
    bl_label = 'Compile All Shaders'
    bl_label = 'Compile All OSL Shader Scripts'
    bl_options = {'REGISTER', 'UNDO'}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        if not compile_all_shaders():
            self.report({'ERROR'}, 'Failed to compile osl file.')

            return {'CANCELLED'}

        register_shaders()

        return {'FINISHED'}
