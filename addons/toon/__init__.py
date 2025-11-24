bl_info = {
    'name': 'Toon',
    'author': 'gnya',
    'version': (0, 1, 9),
    'blender': (3, 6, 0),
    'description':
        'Add shader script wrappers and other features '
        'to make the toon shader easier to use. (For my personal project.)',
    'category': 'Material'
}


from . import manager
from . import nodes
from . import ops
from . import props
from . import shaders
from . import ui


def register():
    props.register()
    manager.register()
    ops.register()
    ui.register()
    shaders.register()
    nodes.register()


def unregister():
    props.unregister()
    manager.unregister()
    ops.unregister()
    ui.unregister()
    shaders.unregister()
    nodes.unregister()
