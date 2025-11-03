import os


def script_abs_path(script_name):
    addon_path = os.path.dirname(os.path.abspath(__file__))

    return f'{addon_path}\\{script_name}.osl'
