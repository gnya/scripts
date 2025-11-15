from . import palette

from .ops_add_remove import (
    VIEW3D_OT_toon_add_palette,
    VIEW3D_OT_toon_remove_palette,
    VIEW3D_OT_toon_add_palette_group,
    VIEW3D_OT_toon_remove_palette_group,
    VIEW3D_OT_toon_add_palette_entry,
    VIEW3D_OT_toon_remove_palette_entry
)
from .ops_convert import VIEW3D_OT_toon_convert_palette
from .ops_copy_paste import VIEW3D_OT_toon_copy_palette
from .ops_copy_paste import VIEW3D_OT_toon_paste_palette
from .ops_move import VIEW3D_OT_toon_move_palette
from .ops_move import VIEW3D_OT_toon_move_palette_slot
from .panels import VIEW3D_UL_toon_palette_entry
from .panels import VIEW3D_MT_toon_palette_menu
from .panels import VIEW3D_MT_toon_palette_group_menu
from .panels import VIEW3D_PT_toon_palette


classes = (
    VIEW3D_OT_toon_add_palette,
    VIEW3D_OT_toon_remove_palette,
    VIEW3D_OT_toon_add_palette_group,
    VIEW3D_OT_toon_remove_palette_group,
    VIEW3D_OT_toon_add_palette_entry,
    VIEW3D_OT_toon_remove_palette_entry,
    VIEW3D_OT_toon_convert_palette,
    VIEW3D_OT_toon_copy_palette,
    VIEW3D_OT_toon_paste_palette,
    VIEW3D_OT_toon_move_palette,
    VIEW3D_OT_toon_move_palette_slot,
    VIEW3D_UL_toon_palette_entry,
    VIEW3D_MT_toon_palette_menu,
    VIEW3D_MT_toon_palette_group_menu,
    VIEW3D_PT_toon_palette
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
