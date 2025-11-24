from toon.utils import override

from bpy.types import Context, Menu, Node, UILayout

from toon.nodes import PaletteNode
from toon.nodes import ToonNodeMatCap
from toon.nodes import ToonNodeVisualize
from toon.nodes import ToonNodeHSVJitter
from toon.nodes import ToonNodeUVPixelSnap
from toon.nodes import ToonNodeLambert
from toon.nodes import ToonNodeMaterial
from toon.nodes import ToonNodeAreaLight
from toon.nodes import ToonNodePointLight
from toon.nodes import ToonNodeSpotLight
from toon.nodes import ToonNodeSunLight
from toon.nodes import ToonNodeOutput


class NODE_MT_toon_node_category(Menu):
    bl_idname = 'NODE_MT_category_toon'
    bl_label = 'Toon'
    bl_space_type = 'NODE_EDITOR'

    @classmethod
    @override
    def poll(cls, context: Context) -> bool:
        return (
            context.space_data.type == 'NODE_EDITOR' and
            context.space_data.tree_type == 'ShaderNodeTree' and
            context.scene.render.engine == 'CYCLES' and
            context.scene.cycles.shading_system
        )

    def _draw_item(self, layout: UILayout, type: type):
        bl_rna = Node.bl_rna_get_subclass(type.__name__)

        if bl_rna is not None:
            label = bl_rna.name
        else:
            label = 'Unknown'

        o = layout.operator('node.add_node', text=label)
        o.type = type.__name__
        o.use_transform = True

    @override
    def draw(self, context: Context):
        layout = self.layout

        col = layout.column(align=True)
        self._draw_item(col, PaletteNode)
        col.separator()
        self._draw_item(col, ToonNodeMatCap)
        self._draw_item(col, ToonNodeVisualize)
        self._draw_item(col, ToonNodeHSVJitter)
        self._draw_item(col, ToonNodeUVPixelSnap)
        col.separator()
        self._draw_item(col, ToonNodeLambert)
        self._draw_item(col, ToonNodeMaterial)
        col.separator()
        self._draw_item(col, ToonNodeAreaLight)
        self._draw_item(col, ToonNodePointLight)
        self._draw_item(col, ToonNodeSpotLight)
        self._draw_item(col, ToonNodeSunLight)
        col.separator()
        self._draw_item(col, ToonNodeOutput)

    @classmethod
    def register(cls):
        from nodeitems_utils import _node_categories

        def _draw(self: Menu, context: Context):
            layout = self.layout

            if cls.poll(context):
                layout.menu(cls.bl_idname)

        _node_categories['SHADER_TOON'] = ([], _draw, [cls])

    @staticmethod
    def unregister():
        from nodeitems_utils import _node_categories

        del _node_categories['SHADER_TOON']
