from __future__ import annotations

from typing import TYPE_CHECKING

from bpy.types import Operator

from toon.shaders import compile_all_shaders, register_shaders
from toon.utils import all_node_itr, override

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems
    from bpy.types import Context


class NODE_OT_toon_node_reload_all(Operator):
    bl_idname = "node.toon_node_reload_all"
    bl_label = "Reload All Nodes"
    bl_description = "Reload all toon nodes"
    bl_options = {"REGISTER", "UNDO"}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        for node in all_node_itr():
            if hasattr(node, "reload"):
                node.reload()

        return {"FINISHED"}


class NODE_OT_toon_node_compile_all(Operator):
    bl_idname = "node.toon_node_compile_all"
    bl_label = "Compile All Shaders"
    bl_description = "Compile all OSL shader scripts"
    bl_options = {"REGISTER", "UNDO"}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        if not compile_all_shaders():
            self.report({"ERROR"}, "Failed to compile osl file.")

            return {"CANCELLED"}

        register_shaders()

        return {"FINISHED"}


class NODE_OT_toon_node_setup_osl_render(Operator):
    bl_idname = "node.toon_node_setup_osl_render"
    bl_label = "Setup OSL Render"
    bl_description = "Set up Cycles render settings for OSL"
    bl_options = {"REGISTER", "UNDO"}

    @override
    def execute(self, context: Context) -> set[OperatorReturnItems]:
        scene = context.scene

        scene.render.engine = "CYCLES"
        scene.cycles.device = "CPU"
        scene.cycles.shading_system = True
        scene.cycles.use_preview_adaptive_sampling = False
        scene.cycles.preview_samples = 1
        scene.cycles.use_preview_denoising = False
        scene.cycles.use_adaptive_sampling = False
        scene.cycles.samples = 1
        scene.cycles.use_denoising = False
        scene.cycles.min_light_bounces = 0
        scene.cycles.min_transparent_bounces = 16
        scene.cycles.max_bounces = 0
        scene.cycles.diffuse_bounces = 0
        scene.cycles.glossy_bounces = 0
        scene.cycles.transmission_bounces = 0
        scene.cycles.volume_bounces = 0
        scene.cycles.transparent_max_bounces = 16
        scene.cycles.sample_clamp_direct = 0.0
        scene.cycles.sample_clamp_indirect = 1.0e-10
        scene.cycles.pixel_filter_type = "BLACKMAN_HARRIS"
        scene.cycles.filter_width = 0.01
        scene.display_settings.display_device = "sRGB"
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.look = "None"
        scene.view_settings.exposure = 0.0
        scene.view_settings.gamma = 1.0
        scene.render.dither_intensity = 0.0

        return {"FINISHED"}
