from .node_menu import NODE_MT_toon_node_category
from .node_panel import VIEW3D_PT_toon_node
from .node_panel import MATERIAL_PT_toon_node
from .node_panel import OBJECT_PT_toon_node
from .palette_menu import VIEW3D_MT_toon_palette_add
from .palette_menu import VIEW3D_MT_toon_palette
from .palette_menu import VIEW3D_MT_toon_palette_group
from .palette_list import VIEW3D_UL_toon_palette_entry
from .palette_panel import VIEW3D_PT_toon_palette


classes = (
    NODE_MT_toon_node_category,
    VIEW3D_PT_toon_node,
    MATERIAL_PT_toon_node,
    OBJECT_PT_toon_node,
    VIEW3D_MT_toon_palette_add,
    VIEW3D_MT_toon_palette,
    VIEW3D_MT_toon_palette_group,
    VIEW3D_UL_toon_palette_entry,
    VIEW3D_PT_toon_palette
)


def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)
