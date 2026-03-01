from __future__ import annotations

from os.path import exists, realpath
from typing import TYPE_CHECKING, Any

import bpy
from bpy.path import abspath

from .bridge import color_types

if TYPE_CHECKING:
    from .core import ToonPalette, ToonPaletteColor, ToonPaletteFacade, ToonPaletteGroup

    SerializedData = tuple[str, dict[str, Any]]
    TexturePtr = tuple[Any, str]

_IMAGE_DATA_PROPS = {
    "display_aspect",
    "file_format",
    "filepath",
    "filepath_raw",
    "generated_color",
    "generated_height",
    "generated_type",
    "generated_width",
    "resolution",
    "seam_margin",
    "source",
    "use_deinterlace",
    "use_generated_float",
    "use_half_precision",
    "use_multiview",
    "use_view_as_render",
    "views_format",
}


class PaletteDecodeError(ValueError):
    pass


def _parse_data(data: Any) -> SerializedData:
    match data:
        case (str(name), dict(body)):
            return name, body
        case _:
            raise PaletteDecodeError("Invalid palette data.")


def encode_texture(texture_ptr: TexturePtr) -> SerializedData:
    image = getattr(*texture_ptr, None)

    if image is None:
        return "", {}

    name, data = image.name, {}
    data["name"] = name

    for prop in _IMAGE_DATA_PROPS:
        value = getattr(image, prop)

        if isinstance(value, str):
            if "filepath" in prop:
                data[prop] = realpath(abspath(value))
            else:
                data[prop] = value
        elif hasattr(value, "__getitem__"):
            data[prop] = list(value)
        else:
            data[prop] = value

    return name, data


def encode_color(color: ToonPaletteColor) -> SerializedData:
    name, data = color.name, {}
    type = color.type
    data["type"] = type

    if type == "COLOR":
        data["color"] = list(getattr(*color.color_ptr))
    elif type == "TEXTURE":
        data["texture"] = encode_texture(color.texture_ptr)
        data["uv_map"] = getattr(*color.uv_map_ptr)
    elif type == "VECTOR":
        data["vector"] = list(getattr(*color.color_ptr))
    elif type == "VALUE":
        data["value"] = getattr(*color.color_ptr)

    return name, data


def encode_group(group: ToonPaletteGroup) -> SerializedData:
    return group.name, dict([encode_color(c) for c in group.colors()])


def encode_palette(palette: ToonPalette) -> SerializedData:
    return palette.name, dict([encode_group(g) for g in palette.groups()])


def decode_texture(data: SerializedData, texture_ptr: TexturePtr):
    name, body = _parse_data(data)

    if name == "":
        return

    image = bpy.data.images.get(name)
    filepath = body.get("filepath_raw", "")

    if image is None or (
        filepath and filepath != realpath(abspath(image.filepath_raw))
    ):
        if filepath and exists(filepath):
            image = bpy.data.images.load(filepath)
        else:
            image = bpy.data.images.new(name, 1024, 1024)

        for prop in _IMAGE_DATA_PROPS:
            if prop in body:
                setattr(image, prop, body[prop])

    setattr(*texture_ptr, image)


def decode_color(data: SerializedData, group: ToonPaletteGroup):
    name, body = _parse_data(data)
    color = group.add(name)

    type = body.get("type", "COLOR")

    if type not in [t[0] for t in color_types()]:
        raise PaletteDecodeError(f"Invalid color type. : {type}")

    color.type = type

    if type == "COLOR":
        setattr(*color.color_ptr, body.get("color", (1.0, 1.0, 1.0, 1.0)))
    elif type == "TEXTURE":
        decode_texture(body.get("texture", {}), color.texture_ptr)
        setattr(*color.uv_map_ptr, body.get("uv_map", ""))
    elif type == "VECTOR":
        setattr(*color.color_ptr, body.get("vector", (0.0, 0.0, 0.0)))
    elif type == "VALUE":
        setattr(*color.color_ptr, body.get("value", 0.0))


def decode_group(data: SerializedData, palette: ToonPalette):
    name, body = _parse_data(data)
    group = palette.add(name)

    for color_name, color_data in body.items():
        decode_color((color_name, color_data), group)


def decode_palette(data: SerializedData, facade: ToonPaletteFacade):
    name, body = _parse_data(data)
    palette = facade.add(name)

    for group_name, group_data in body.items():
        decode_group((group_name, group_data), palette)
