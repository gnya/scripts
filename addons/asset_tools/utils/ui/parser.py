from typing import Any


class ParseContentError(Exception):
    pass


def _parse_operator(
    content: dict[str, Any] | tuple[Any],
) -> tuple[tuple[Any] | None, str, dict[str, Any]]:
    if isinstance(content, tuple):
        return content, "", {}

    c = None
    enum_arg = ""
    args: dict[str, Any] = {}

    for key, value in content.items():
        if isinstance(value, tuple):
            enum_arg, c = key, value
        else:
            args[key] = value

    return c, enum_arg, args


def _parse_operators(
    content_list: list[Any], path: str, content: dict[str, Any] | tuple[Any] | Any
):
    if "." not in path:
        if not isinstance(content, dict):
            raise ParseContentError(f'"{path}": parsing operator was failed.')

        for p, c in content.items():
            _parse_operators(content_list, f"{path}.{p}", c)
    else:
        content_list.append((path, *_parse_operator(content)))


def _parse_properties(
    content_list: list[Any], path: str, content: dict[str, Any] | tuple[Any] | Any
):
    if isinstance(content, dict):
        for p, c in content.items():
            if p.startswith("["):
                _parse_properties(content_list, f"{path}{p}", c)
            else:
                _parse_properties(content_list, f"{path}.{p}", c)
    else:
        if not isinstance(content, tuple):
            raise ParseContentError(f'"{path}": parsing property was failed.')

        content_list.append((path, content))


def parse_contents(
    contents: dict[str, Any] | tuple[dict[str, dict[str, Any] | tuple[Any] | Any]],
) -> list[Any]:
    if isinstance(contents, dict):
        contents = (contents,)

    content_list: list[Any] = []

    for content_dict in contents:
        for path, c in content_dict.items():
            if path.startswith("$"):
                _parse_operators(content_list, path[1:], c)
            else:
                _parse_properties(content_list, path, c)

    return content_list
