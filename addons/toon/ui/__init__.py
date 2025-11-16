from .op_add_remove import (
    VIEW3D_OT_toon_add_palette,
    VIEW3D_OT_toon_remove_palette,
    VIEW3D_OT_toon_add_palette_group,
    VIEW3D_OT_toon_remove_palette_group,
    VIEW3D_OT_toon_add_palette_entry,
    VIEW3D_OT_toon_remove_palette_entry
)
from .op_convert import VIEW3D_OT_toon_convert_palette
from .op_copy_paste import VIEW3D_OT_toon_copy_palette
from .op_copy_paste import VIEW3D_OT_toon_paste_palette
from .op_move import VIEW3D_OT_toon_move_palette
from .op_move import VIEW3D_OT_toon_move_palette_slot
from .ui_palette import VIEW3D_UL_toon_palette_entry
from .ui_palette import VIEW3D_MT_toon_palette_menu
from .ui_palette import VIEW3D_MT_toon_palette_group_menu
from .ui_palette import VIEW3D_PT_toon_palette
from .ui_toon import MATERIAL_PT_toon
from .ui_toon import OBJECT_PT_toon


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
    VIEW3D_PT_toon_palette,
    MATERIAL_PT_toon,
    OBJECT_PT_toon
)


def register():
    from bpy.utils import register_class

    from toon import manager
    from toon.props import ToonSettings

    manager.register()
    register_class(ToonSettings)

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    from toon import manager
    from toon.props import ToonSettings

    manager.unregister()
    unregister_class(ToonSettings)

    for c in classes:
        unregister_class(c)
