from .toon_settings import ToonSettings


__all__ = [
    ToonSettings
]


classes = (
    ToonSettings,
)


def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)
