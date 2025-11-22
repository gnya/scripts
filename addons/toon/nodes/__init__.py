from .palette import PaletteNode

from .matcap import ToonNodeMatCap
from .visualize import ToonNodeVisualize

from .hsv_jitter import ToonNodeHSVJitter
from .uv_pixel_snap import ToonNodeUVPixelSnap
from .lambert import ToonNodeLambert
from .material import ToonNodeMaterial

from .area_light import ToonNodeAreaLight
from .point_light import ToonNodePointLight
from .spot_light import ToonNodeSpotLight
from .sun_light import ToonNodeSunLight

from .output import ToonNodeOutput


node_classes = (
    PaletteNode,
    ToonNodeMatCap,
    ToonNodeVisualize,
    ToonNodeHSVJitter,
    ToonNodeUVPixelSnap,
    ToonNodeLambert,
    ToonNodeMaterial,
    ToonNodeAreaLight,
    ToonNodePointLight,
    ToonNodeSpotLight,
    ToonNodeSunLight,
    ToonNodeOutput
)


def register():
    from bpy.utils import register_class
    from nodeitems_utils import NodeItem, register_node_categories

    from .base import ToonNodeCategory

    for c in node_classes:
        register_class(c)

    toon_nodes = []

    for c in node_classes:
        toon_nodes.append(NodeItem(c.__name__))

    cat = ToonNodeCategory('TOON', 'Toon', items=toon_nodes)
    register_node_categories('TOON', [cat])


def unregister():
    from bpy.utils import unregister_class
    from nodeitems_utils import unregister_node_categories

    for c in node_classes:
        unregister_class(c)

    unregister_node_categories('TOON')
