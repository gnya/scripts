from rig import color
from rig import ik_fk
from rig import props
from rig import tools


bl_info = {
    'name': 'Rig',
    'author': 'gnya',
    'version': (0, 1, 15),
    'blender': (3, 6, 0),
    'description':
        'A set of tools to make assets easier to use. '
        '(For my personal project.)',
    'category': 'Utility'
}


def register():
    color.register()
    tools.register()
    props.register()
    ik_fk.register()


def unregister():
    color.unregister()
    tools.unregister()
    props.unregister()
    ik_fk.unregister()


if __name__ == '__main__':
    register()
