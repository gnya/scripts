from typing import Any

from toon.props import Palette, PaletteEntry, PaletteGroup

from .image import decode_image, encode_image


EntryData = dict[str, Any]
GroupData = dict[str, EntryData]
PaletteData = dict[str, GroupData]


class PaletteParseError(Exception):
    pass


def encode_entry(entry: PaletteEntry) -> EntryData:
    data: EntryData = {'type': entry.type}

    if entry.type == 'COLOR':
        data['color'] = list(entry.color)
    elif entry.type == 'TEXTURE':
        node = entry.node()
        image = None if node is None else node.image
        data['texture_image'] = encode_image(image)
    elif entry.type == 'MIX':
        data['mix_factor'] = entry.mix_factor
        data['mix_source_a'] = entry.mix_source_a
        data['mix_source_b'] = entry.mix_source_b

    return data


def decode_entry(data: EntryData, entry: PaletteEntry):
    entry.type = data['type']

    if entry.type == 'COLOR':
        entry.color = data.get('color', (1.0, 1.0, 1.0, 1.0))
    elif entry.type == 'TEXTURE':
        node = entry.node()

        if node is not None:
            node.image = decode_image(data.get('texture_image', {}))
    elif entry.type == 'MIX':
        entry.mix_factor = data.get('mix_factor', 0.0)
        entry.mix_source_a = data.get('mix_source_a', '')
        entry.mix_source_b = data.get('mix_source_b', '')


def encode_group(group: PaletteGroup) -> GroupData:
    data: GroupData = {}

    for entry_name, entry in group.entries.items():
        data[entry_name] = encode_entry(entry)

    return data


def decode_group(data: GroupData, group: PaletteGroup, forced: bool = False):
    if forced:
        group.clear()

    for entry_name, entry_data in data.items():
        entry = group.get_entry(entry_name)

        if entry is None:
            entry = group.add(entry_name)

        decode_entry(entry_data, entry)

    # Solve `MIX` type entry.
    for entry_name, entry in group.entries.items():
        if entry.type == 'MIX':
            entry.mix_source_a = entry.mix_source_a
            entry.mix_source_b = entry.mix_source_b


def encode_palette(palette: Palette) -> PaletteData:
    data: PaletteData = {}

    for group_name, group in palette.entries.items():
        data[group_name] = encode_group(group)

    return data


def decode_palette(data: PaletteData, palette: Palette, forced: bool = False):
    if forced:
        palette.clear()

    for group_name, group_data in data.items():
        group = palette.get_entry(group_name)

        if group is None:
            group = palette.add(group_name)

        decode_group(group_data, group, forced)
