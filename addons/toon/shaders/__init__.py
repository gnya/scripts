def script_path(name: str):
    import os

    path = os.path.dirname(os.path.abspath(__file__))

    return f'{path}\\{name}.osl'
