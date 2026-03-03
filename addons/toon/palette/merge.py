from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import ToonPalette, ToonPaletteColor, ToonPaletteGroup


def merge_color(src: ToonPaletteColor, dst: ToonPaletteColor) -> bool:
    type = src.type
    dst.type = type

    if type == "COLOR":
        setattr(*src.color_ptr, getattr(*dst.color_ptr))
    elif type == "TEXTURE":
        setattr(*src.texture_ptr, getattr(*dst.texture_ptr))
        setattr(*src.uv_map_ptr, getattr(*dst.uv_map_ptr))
    elif type == "VECTOR":
        setattr(*src.color_ptr, getattr(*dst.color_ptr))
    elif type == "VALUE":
        setattr(*src.color_ptr, getattr(*dst.color_ptr))

    return True


def merge_group(
    src: ToonPaletteGroup, dst: ToonPaletteGroup, overwrite: bool = False
) -> bool:
    if src.is_linked or dst.is_linked:
        return False

    for src_color in src.colors():
        if overwrite:
            dst_color = dst.get(src_color.name)
        else:
            dst_color = None

        if dst_color is None:
            dst_color = dst.add(src_color.name)

        merge_color(src_color, dst_color)

    return True


def merge_palette(src: ToonPalette, dst: ToonPalette, overwrite: bool = False) -> bool:
    if src.is_linked or dst.is_linked:
        return False

    for src_group in src.groups():
        if overwrite:
            dst_group = dst.get(src_group.name)
        else:
            dst_group = None

        if dst_group is None:
            dst_group = dst.add(src_group.name)

        merge_group(src_group, dst_group, overwrite)

    return True
