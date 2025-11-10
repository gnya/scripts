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
from .props_ui import (
    PaletteItem, PaletteGroup,
    PaletteUIItem, PaletteUI
)


def register():
    from bpy.props import PointerProperty
    from bpy.types import NodeTree
    from bpy.utils import register_class

    register_class(PaletteItem)
    register_class(PaletteGroup)
    register_class(PaletteUIItem)
    register_class(PaletteUI)

    register_class(VIEW3D_OT_toon_add_palette)
    register_class(VIEW3D_OT_toon_remove_palette)
    register_class(VIEW3D_OT_toon_add_palette_group)
    register_class(VIEW3D_OT_toon_remove_palette_group)
    register_class(VIEW3D_OT_toon_add_palette_item)
    register_class(VIEW3D_OT_toon_remove_palette_item)
    register_class(VIEW3D_OT_toon_move_palette_slot)

    register_class(VIEW3D_UL_toon_palette_item)
    register_class(VIEW3D_PT_toon_palette)

    NodeTree.toon_palette = PointerProperty(type=PaletteUI)


def unregister():
    from bpy.types import NodeTree
    from bpy.utils import unregister_class

    unregister_class(PaletteItem)
    unregister_class(PaletteGroup)
    unregister_class(PaletteUIItem)
    unregister_class(PaletteUI)

    unregister_class(VIEW3D_OT_toon_add_palette)
    unregister_class(VIEW3D_OT_toon_remove_palette)
    unregister_class(VIEW3D_OT_toon_add_palette_group)
    unregister_class(VIEW3D_OT_toon_remove_palette_group)
    unregister_class(VIEW3D_OT_toon_add_palette_item)
    unregister_class(VIEW3D_OT_toon_remove_palette_item)
    unregister_class(VIEW3D_OT_toon_move_palette_slot)

    unregister_class(VIEW3D_UL_toon_palette_item)
    unregister_class(VIEW3D_PT_toon_palette)

    del NodeTree.toon_palette
