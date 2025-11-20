from . import manager
from . import nodes
from . import props
from . import ui


bl_info = {
    'name': 'Toon',
    'author': 'gnya',
    'version': (0, 1, 2),
    'blender': (3, 6, 0),
    'description':
        'Add shader script wrappers and other features '
        'to make the toon shader easier to use. (For my personal project.)',
    'category': 'Material'
}


def register():
    props.register()
    manager.register()
    ui.register()
    nodes.register()


def unregister():
    props.unregister()
    manager.unregister()
    ui.unregister()
    nodes.unregister()


if __name__ == '__main__':
    register()
