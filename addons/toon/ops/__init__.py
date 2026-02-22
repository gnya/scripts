from .node import NODE_OT_toon_node_compile_all
from .node import NODE_OT_toon_node_reload_all
from .node import NODE_OT_toon_node_setup_osl_render


classes = (
    NODE_OT_toon_node_compile_all,
    NODE_OT_toon_node_reload_all,
    NODE_OT_toon_node_setup_osl_render
)


def register():
    from bpy.utils import register_class

    for c in classes:
        register_class(c)


def unregister():
    from bpy.utils import unregister_class

    for c in classes:
        unregister_class(c)
