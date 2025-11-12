from . import palette

from .ops import (
    VIEW3D_OT_toon_add_palette,
    VIEW3D_OT_toon_remove_palette,
    VIEW3D_OT_toon_add_palette_group,
    VIEW3D_OT_toon_remove_palette_group,
    VIEW3D_OT_toon_add_palette_item,
    VIEW3D_OT_toon_remove_palette_item,
    VIEW3D_OT_toon_move_palette_slot
)
from .panels import (
    VIEW3D_UL_toon_palette_item,
    VIEW3D_PT_toon_palette
)


classes = (
    VIEW3D_OT_toon_add_palette,
    VIEW3D_OT_toon_remove_palette,
    VIEW3D_OT_toon_add_palette_group,
    VIEW3D_OT_toon_remove_palette_group,
    VIEW3D_OT_toon_add_palette_item,
    VIEW3D_OT_toon_remove_palette_item,
    VIEW3D_OT_toon_move_palette_slot,
    VIEW3D_UL_toon_palette_item,
    VIEW3D_PT_toon_palette,
)


def register():
    from bpy.utils import register_class

    palette.register()

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    palette.unregister()

    for c in classes:
        unregister_class(c)
