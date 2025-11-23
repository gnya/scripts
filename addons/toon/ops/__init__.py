from .op_add import VIEW3D_OT_toon_add_palette
from .op_add import VIEW3D_OT_toon_add_palette_group
from .op_add import VIEW3D_OT_toon_add_palette_entry
from .op_add_by import VIEW3D_OT_toon_add_palette_by_node_tree
from .op_add_by import VIEW3D_OT_toon_add_palette_by_clipboard
from .op_remove import VIEW3D_OT_toon_remove_palette
from .op_remove import VIEW3D_OT_toon_remove_palette_group
from .op_remove import VIEW3D_OT_toon_remove_palette_entry
from .op_copy_paste import VIEW3D_OT_toon_copy_palette
from .op_copy_paste import VIEW3D_OT_toon_paste_palette
from .op_move import VIEW3D_OT_toon_move_palette
from .op_move import VIEW3D_OT_toon_move_palette_slot


classes = (
    VIEW3D_OT_toon_add_palette,
    VIEW3D_OT_toon_add_palette_group,
    VIEW3D_OT_toon_add_palette_entry,
    VIEW3D_OT_toon_add_palette_by_node_tree,
    VIEW3D_OT_toon_add_palette_by_clipboard,
    VIEW3D_OT_toon_remove_palette,
    VIEW3D_OT_toon_remove_palette_group,
    VIEW3D_OT_toon_remove_palette_entry,
    VIEW3D_OT_toon_copy_palette,
    VIEW3D_OT_toon_paste_palette,
    VIEW3D_OT_toon_move_palette,
    VIEW3D_OT_toon_move_palette_slot,
)


def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)
