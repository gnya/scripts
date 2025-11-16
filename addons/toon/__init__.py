from . import ui
from . import nodes


bl_info = {
    'name': 'Toon',
    'author': 'gnya',
    'version': (0, 0, 16),
    'blender': (3, 6, 0),
    'description':
        'Add shader script wrappers and other features '
        'to make the toon shader easier to use. (For my personal project.)',
    'category': 'Material'
}


def register():
    ui.register()
    nodes.register()


def unregister():
    ui.unregister()
    nodes.unregister()


if __name__ == '__main__':
    register()
