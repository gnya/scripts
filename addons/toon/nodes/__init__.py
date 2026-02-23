from .palette import ToonNodePalette

from .matcap import ToonNodeMatCap
from .visualize import ToonNodeVisualize

from .hsv_jitter import ToonNodeHSVJitter
from .uv_pixel_snap import ToonNodeUVPixelSnap
from .lambert import ToonNodeLambert
from .material import ToonNodeMaterial

from .area_light import ToonNodeLightArea
from .point_light import ToonNodeLightPoint
from .spot_light import ToonNodeLightSpot
from .sun_light import ToonNodeLightSun

from .output import ToonNodeOutput


classes = (
    ToonNodePalette,
    ToonNodeMatCap,
    ToonNodeVisualize,
    ToonNodeHSVJitter,
    ToonNodeUVPixelSnap,
    ToonNodeLambert,
    ToonNodeMaterial,
    ToonNodeLightArea,
    ToonNodeLightPoint,
    ToonNodeLightSpot,
    ToonNodeLightSun,
    ToonNodeOutput
)


def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)
