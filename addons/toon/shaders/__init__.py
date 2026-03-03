from .shaders import (
    compile_all_shaders,
    register_shaders,
    shader_filepath,
    unregister_shaders,
)

__all__ = [shader_filepath, compile_all_shaders, register_shaders, unregister_shaders]


def register():
    from toon.utils import register_pid

    from .shaders import SHADER_PREFIX

    register_pid(SHADER_PREFIX)
    register_shaders()


def unregister():
    from toon.utils import list_pids, unregister_pid

    from .shaders import SHADER_PREFIX

    unregister_pid(SHADER_PREFIX)

    if not list_pids(SHADER_PREFIX):
        unregister_shaders()
