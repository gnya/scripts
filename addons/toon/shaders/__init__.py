SHADER_PREFIX = 'toon_addon'


def script_filepath(name: str) -> str:
    return f'{SHADER_PREFIX}_{name}'


def register():
    import os
    import shutil

    from bpy.utils import resource_path
    from _cycles import osl_compile  # type: ignore

    scripts_path = os.path.dirname(os.path.abspath(__file__))
    shaders_path = f"{resource_path('USER')}\\shaders"

    os.makedirs(shaders_path, exist_ok=True)

    for filename in os.listdir(scripts_path):
        if filename.endswith('.osl'):
            basename = filename.rsplit('.')[0]
            src_path = f'{scripts_path}\\{basename}.oso'
            dst_path = f'{shaders_path}\\{SHADER_PREFIX}_{basename}.oso'

            if os.path.exists(src_path):
                shutil.copy(src_path, dst_path)
            elif osl_compile(f'{scripts_path}\\{filename}', src_path):
                shutil.copy(src_path, dst_path)
            else:
                print(f'{filename}: Failed to compile this osl file.')


def unregister():
    import os
    import shutil

    from bpy.utils import resource_path

    shaders_path = f"{resource_path('USER')}\\shaders"

    for filename in os.listdir(shaders_path):
        if filename.startswith(SHADER_PREFIX) and filename.endswith('.oso'):
            os.remove(f'{shaders_path}\\{filename}')

    if len(os.listdir(shaders_path)) == 0:
        shutil.rmtree(shaders_path)
