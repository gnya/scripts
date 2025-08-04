class ParseContentError(Exception):
    pass


def _collect_operator(content: dict | tuple) -> tuple[tuple, str, dict]:
    if isinstance(content, tuple):
        return content, '', {}

    c = set()
    enum_arg = ''
    args = {}

    for key, value in content.items():
        if isinstance(value, tuple):
            enum_arg, c = key, value
        else:
            args[key] = value

    return c, enum_arg, args


def _collect_operators(content_list: list, path: str, content: dict | tuple):
    if '.' not in path:
        if not isinstance(content, dict):
            raise ParseContentError(f'"{path}": parsing operator was failed.')

        for p, c in content.items():
            _collect_operators(content_list, f'{path}.{p}', c)
    else:
        content_list.append((path, *_collect_operator(content)))


def _collect_properties(content_list: list, path: str, content: dict | tuple):
    if isinstance(content, dict):
        for p, c in content.items():
            if p.startswith('['):
                _collect_properties(content_list, f'{path}{p}', c)
            else:
                _collect_properties(content_list, f'{path}.{p}', c)
    else:
        if not isinstance(content, tuple):
            raise ParseContentError(f'"{path}": parsing property was failed.')

        content_list.append((path, content))


def _collect_contents(contents: dict | tuple[dict]) -> list:
    if isinstance(contents, dict):
        contents = (contents,)

    content_list = []

    for content_dict in contents:
        for path, c in content_dict.items():
            if path.startswith('$'):
                _collect_operators(content_list, path[1:], c)
            else:
                _collect_properties(content_list, path, c)

    return content_list
