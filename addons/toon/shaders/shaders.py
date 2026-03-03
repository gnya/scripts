import os
import shutil

from _cycles import osl_compile  # type: ignore
from bpy.utils import resource_path

SHADER_PREFIX = "toon_addon"
SCRIPTS_PATH = os.path.dirname(os.path.abspath(__file__))
SHADERS_PATH = f"{resource_path('USER')}\\shaders"


def shader_filepath(name: str) -> str:
    return f"{SHADER_PREFIX}_{name}"


def compile_all_shaders() -> bool:
    for filename in os.listdir(SCRIPTS_PATH):
        if filename.endswith(".osl"):
            basename = filename.rsplit(".")[0]
            src_path = f"{SCRIPTS_PATH}\\{basename}.oso"

            if not osl_compile(f"{SCRIPTS_PATH}\\{filename}", src_path):
                print(f"Failed to compile this OSL script. : {filename}")

                return False

    return True


def register_shaders():
    os.makedirs(SHADERS_PATH, exist_ok=True)

    for filename in os.listdir(SCRIPTS_PATH):
        if filename.endswith(".osl"):
            basename = filename.rsplit(".")[0]
            src_path = f"{SCRIPTS_PATH}\\{basename}.oso"
            dst_path = f"{SHADERS_PATH}\\{SHADER_PREFIX}_{basename}.oso"

            if os.path.exists(src_path):
                shutil.copy(src_path, dst_path)
            elif osl_compile(f"{SCRIPTS_PATH}\\{filename}", src_path):
                shutil.copy(src_path, dst_path)
            else:
                print(f"Failed to compile this OSL script. : {filename}")


def unregister_shaders():
    for filename in os.listdir(SHADERS_PATH):
        if filename.startswith(SHADER_PREFIX) and filename.endswith(".oso"):
            os.remove(f"{SHADERS_PATH}\\{filename}")

    if len(os.listdir(SHADERS_PATH)) == 0:
        shutil.rmtree(SHADERS_PATH)
