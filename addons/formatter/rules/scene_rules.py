from . import utils
from .rules import Report, SceneRule


class ToonScenePropertiesRule(SceneRule):
    @classmethod
    def fix_scene(cls, scene, **kwargs):
        resetted = utils.reset_properties(scene, {
            'render.engine': 'CYCLES',
            'cycles.device': 'CPU',
            'cycles.shading_system': True,
            'cycles.use_preview_adaptive_sampling': False,
            'cycles.preview_samples': 1,
            'cycles.use_preview_denoising': False,
            'cycles.use_adaptive_sampling': False,
            'cycles.samples': 1,
            'cycles.use_denoising': False,
            'cycles.min_light_bounces': 0,
            'cycles.min_transparent_bounces': 16,
            'cycles.max_bounces': 0,
            'cycles.diffuse_bounces': 0,
            'cycles.glossy_bounces': 0,
            'cycles.transmission_bounces': 0,
            'cycles.volume_bounces': 0,
            'cycles.transparent_max_bounces': 16,
            'cycles.sample_clamp_direct': 0.0,
            'cycles.sample_clamp_indirect': 1.000000013351432e-10,
            'cycles.pixel_filter_type': 'BLACKMAN_HARRIS',
            'cycles.filter_width': 0.009999999776482582,
            'display_settings.display_device': 'sRGB',
            'view_settings.view_transform': 'Standard',
            'view_settings.look': 'None',
            'view_settings.exposure': 0.0,
            'view_settings.gamma': 1.0,
            'render.dither_intensity': 0.0,
        })

        if resetted:
            s = ', '.join(resetted)

            return Report.log(f'Change scene properties: {s}')

        return Report.nothing()
