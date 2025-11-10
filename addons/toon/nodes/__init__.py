from .matcap import ToonNodeMatCap
from .palette import ToonNodePalette
from .visualize import ToonNodeVisualize

from .material import ToonNodeMaterial

from .area_light import ToonNodeAreaLight
from .point_light import ToonNodePointLight
from .spot_light import ToonNodeSpotLight
from .sun_light import ToonNodeSunLight

from .output import ToonNodeOutput


node_classes = (
    ToonNodeMatCap,
    ToonNodePalette,
    ToonNodeVisualize,
    ToonNodeMaterial,
    ToonNodeAreaLight,
    ToonNodePointLight,
    ToonNodeSpotLight,
    ToonNodeSunLight,
    ToonNodeOutput
)


def register():
    from bpy.utils import register_class
    from nodeitems_utils import NodeItem, NodeCategory, register_node_categories

    for c in node_classes:
        register_class(c)

    toon_nodes = []

    for c in node_classes:
        toon_nodes.append(NodeItem(c.__name__))

    class ToonNodeCategory(NodeCategory):
        @classmethod
        def poll(cls, context):
            return (
                context.space_data.type == 'NODE_EDITOR' and
                context.space_data.tree_type == 'ShaderNodeTree' and
                context.scene.render.engine == 'CYCLES' and
                context.scene.cycles.shading_system
            )

    cat = ToonNodeCategory('TOON', 'Toon', items=toon_nodes)
    register_node_categories('TOON', [cat])


def unregister():
    from bpy.utils import unregister_class
    from nodeitems_utils import unregister_node_categories

    for c in node_classes:
        unregister_class(c)

    unregister_node_categories('TOON')
