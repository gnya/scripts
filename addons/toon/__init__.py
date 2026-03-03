bl_info = {
    "name": "Toon",
    "author": "gnya",
    "version": (0, 2, 0),
    "blender": (3, 6, 0),
    "description": "Add shader script wrappers and other features "
    "to make the toon shader easier to use. (For my personal project.)",
    "category": "Material",
}


from . import nodes, ops, props, shaders, ui, utils


def register():
    utils.register()
    props.register()
    ops.register()
    ui.register()
    shaders.register()
    nodes.register()


def unregister():
    utils.unregister()
    props.unregister()
    ops.unregister()
    ui.unregister()
    shaders.unregister()
    nodes.unregister()
