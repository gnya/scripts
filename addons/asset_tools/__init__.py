from . import color
from . import rig


bl_info = {
    'name': 'Asset Tools',
    'author': 'gnya',
    'version': (0, 2, 1),
    'blender': (3, 6, 0),
    'description':
        'A set of tools to make assets easier to use. '
        '(For my personal project.)',
    'category': 'Utility'
}


def register():
    color.register()
    rig.register()


def unregister():
    color.unregister()
    rig.unregister()


if __name__ == '__main__':
    register()
