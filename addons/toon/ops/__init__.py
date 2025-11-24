from .add import VIEW3D_OT_toon_palette_add
from .add import VIEW3D_OT_toon_palette_add_group
from .add import VIEW3D_OT_toon_palette_add_entry
from .add_by import VIEW3D_OT_toon_palette_add_by_node_tree
from .add_by import VIEW3D_OT_toon_palette_add_by_clipboard
from .remove import VIEW3D_OT_toon_palette_remove
from .remove import VIEW3D_OT_toon_palette_remove_group
from .remove import VIEW3D_OT_toon_palette_remove_entry
from .copy_paste import VIEW3D_OT_toon_palette_copy
from .copy_paste import VIEW3D_OT_toon_palette_paste
from .move import VIEW3D_OT_toon_palette_move
from .move import VIEW3D_OT_toon_palette_move_slot


classes = (
    VIEW3D_OT_toon_palette_add,
    VIEW3D_OT_toon_palette_add_group,
    VIEW3D_OT_toon_palette_add_entry,
    VIEW3D_OT_toon_palette_add_by_node_tree,
    VIEW3D_OT_toon_palette_add_by_clipboard,
    VIEW3D_OT_toon_palette_remove,
    VIEW3D_OT_toon_palette_remove_group,
    VIEW3D_OT_toon_palette_remove_entry,
    VIEW3D_OT_toon_palette_copy,
    VIEW3D_OT_toon_palette_paste,
    VIEW3D_OT_toon_palette_move,
    VIEW3D_OT_toon_palette_move_slot,
)


def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)
