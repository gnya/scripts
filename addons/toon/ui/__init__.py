from .mt_nodes import NODE_MT_category_toon
from .mt_palette import VIEW3D_MT_toon_palette_add_menu
from .mt_palette import VIEW3D_MT_toon_palette_menu
from .mt_palette import VIEW3D_MT_toon_palette_group_menu
from .pt_palette import VIEW3D_PT_toon_palette
from .pt_toon import MATERIAL_PT_toon
from .pt_toon import OBJECT_PT_toon
from .ul_palette import VIEW3D_UL_toon_palette_entry


classes = (
    NODE_MT_category_toon,
    VIEW3D_MT_toon_palette_add_menu,
    VIEW3D_MT_toon_palette_menu,
    VIEW3D_MT_toon_palette_group_menu,
    VIEW3D_UL_toon_palette_entry,
    VIEW3D_PT_toon_palette,
    MATERIAL_PT_toon,
    OBJECT_PT_toon
)


def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)
