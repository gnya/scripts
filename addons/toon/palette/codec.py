from __future__ import annotations

from os.path import exists, realpath
from typing import TYPE_CHECKING, Any

import bpy
from bpy.path import abspath

from .bridge import get_facade

if TYPE_CHECKING:
    from bpy.types import Image

    from .core import ToonPalette, ToonPaletteColor, ToonPaletteGroup

    ImageData = dict[str, Any]
    ColorData = dict[str, ImageData | Any]
    ColorsData = dict[str, ColorData]
    GroupsData = dict[str, ColorsData]
    PaletteData = tuple[str, GroupsData]

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


def encode_texture(image: Image | None) -> ImageData:
    if image is None:
        return {}

    data: ImageData = {}
    data["name"] = image.name

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

    return data


def encode_color(color: ToonPaletteColor) -> ColorData:
    data: ColorData = {}
    type = color.type
    data["type"] = type

    if type == "COLOR":
        data["color"] = list(getattr(*color.color_ptr))
    elif type == "TEXTURE":
        data["texture"] = encode_texture(getattr(*color.texture_ptr))
        data["uv_map"] = getattr(*color.uv_map_ptr)
    elif type == "VECTOR":
        data["vector"] = list(getattr(*color.color_ptr))
    elif type == "VALUE":
        data["value"] = getattr(*color.color_ptr)

    return data


def encode_group(group: ToonPaletteGroup) -> ColorsData:
    return {color.name: encode_color(color) for color in group.colors()}


def encode_palette(palette: ToonPalette) -> GroupsData:
    return {group.name: encode_group(group) for group in palette.groups()}


def encode(palette: ToonPalette) -> PaletteData:
    return palette.name, encode_palette(palette)


def decode_texture(data: ImageData) -> Image | None:
    if "name" not in data:
        return None

    name = data["name"]
    image = bpy.data.images.get(name)
    filepath = data.get("filepath_raw", "")

    if image is None or (
        filepath and filepath != realpath(abspath(image.filepath_raw))
    ):
        if filepath and exists(filepath):
            image = bpy.data.images.load(filepath)
        else:
            image = bpy.data.images.new(name, 1024, 1024)

        for prop in _IMAGE_DATA_PROPS:
            if prop in data:
                setattr(image, prop, data[prop])

    return image


def decode_color(data: ColorData, color: ToonPaletteColor):
    type = data.get("type", "COLOR")
    color.type = type

    if type == "COLOR":
        setattr(*color.color_ptr, data.get("color", (1.0, 1.0, 1.0, 1.0)))
    elif type == "TEXTURE":
        setattr(*color.texture_ptr, decode_texture(data.get("texture", {})))
        setattr(*color.uv_map_ptr, data.get("uv_map", ""))
    elif type == "VECTOR":
        setattr(*color.color_ptr, data.get("vector", (0.0, 0.0, 0.0)))
    elif type == "VALUE":
        setattr(*color.color_ptr, data.get("value", 0.0))


def decode_group(data: ColorsData, group: ToonPaletteGroup):
    for color_name, color_data in data.items():
        decode_color(color_data, group.add(color_name))


def decode_palette(data: GroupsData, palette: ToonPalette):
    for group_name, group_data in data.items():
        decode_group(group_data, palette.add(group_name))


def decode(data: Any):
    if (
        isinstance(data, list)
        and len(data) == 2
        and isinstance(data[0], str)
        and isinstance(data[1], dict)
    ):
        decode_palette(data[1], get_facade().add(data[0]))
