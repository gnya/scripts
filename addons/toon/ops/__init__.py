from .node import (
    NODE_OT_toon_node_compile_all,
    NODE_OT_toon_node_reload_all,
    NODE_OT_toon_node_setup_osl_render,
)
from .palette import (
    VIEW3D_OT_toon_palette_add,
    VIEW3D_OT_toon_palette_add_color,
    VIEW3D_OT_toon_palette_add_group,
    VIEW3D_OT_toon_palette_copy,
    VIEW3D_OT_toon_palette_move,
    VIEW3D_OT_toon_palette_move_item,
    VIEW3D_OT_toon_palette_paste,
    VIEW3D_OT_toon_palette_remove,
    VIEW3D_OT_toon_palette_remove_color,
    VIEW3D_OT_toon_palette_remove_group,
)

classes = (
    NODE_OT_toon_node_compile_all,
    NODE_OT_toon_node_reload_all,
    NODE_OT_toon_node_setup_osl_render,
    VIEW3D_OT_toon_palette_add,
    VIEW3D_OT_toon_palette_remove,
    VIEW3D_OT_toon_palette_add_group,
    VIEW3D_OT_toon_palette_remove_group,
    VIEW3D_OT_toon_palette_add_color,
    VIEW3D_OT_toon_palette_remove_color,
    VIEW3D_OT_toon_palette_copy,
    VIEW3D_OT_toon_palette_paste,
    VIEW3D_OT_toon_palette_move,
    VIEW3D_OT_toon_palette_move_item,
)


def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)
