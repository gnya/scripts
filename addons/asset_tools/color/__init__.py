from .ops import VIEW3D_OT_color_attach_light

from .panels import VIEW3D_PT_color


classes = (
    VIEW3D_OT_color_attach_light,
    VIEW3D_PT_color
)


def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)
