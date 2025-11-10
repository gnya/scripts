from . import props

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


def register():
    from bpy.utils import register_class

    register_class(VIEW3D_OT_toon_add_palette)
    register_class(VIEW3D_OT_toon_remove_palette)
    register_class(VIEW3D_OT_toon_add_palette_group)
    register_class(VIEW3D_OT_toon_remove_palette_group)
    register_class(VIEW3D_OT_toon_add_palette_item)
    register_class(VIEW3D_OT_toon_remove_palette_item)
    register_class(VIEW3D_OT_toon_move_palette_slot)

    register_class(VIEW3D_UL_toon_palette_item)
    register_class(VIEW3D_PT_toon_palette)

    props.register()


def unregister():
    from bpy.utils import unregister_class

    unregister_class(VIEW3D_OT_toon_add_palette)
    unregister_class(VIEW3D_OT_toon_remove_palette)
    unregister_class(VIEW3D_OT_toon_add_palette_group)
    unregister_class(VIEW3D_OT_toon_remove_palette_group)
    unregister_class(VIEW3D_OT_toon_add_palette_item)
    unregister_class(VIEW3D_OT_toon_remove_palette_item)
    unregister_class(VIEW3D_OT_toon_move_palette_slot)

    unregister_class(VIEW3D_UL_toon_palette_item)
    unregister_class(VIEW3D_PT_toon_palette)

    props.unregister()
