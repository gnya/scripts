from typing import Any

import bpy
import os

from bpy.path import abspath
from bpy.types import bpy_prop_array, Image
from mathutils import Vector
from os.path import realpath


_IMAGE_PROPS = {
    'display_aspect', 'file_format', 'filepath',
    'filepath_raw', 'generated_color', 'generated_height',
    'generated_type', 'generated_width', 'resolution',
    'seam_margin', 'source', 'use_deinterlace',
    'use_generated_float', 'use_half_precision',
    'use_multiview', 'use_view_as_render', 'views_format'
}


def _realpath(path: str) -> str:
    return realpath(abspath(path))


def encode_image(image: Image | None) -> dict[str, Any]:
    if image is None:
        return {}

    data = {'name': image.name}

    for prop_name in _IMAGE_PROPS:
        prop = getattr(image, prop_name)

        if isinstance(prop, (bpy_prop_array, Vector)):
            data[prop_name] = list(prop)
        elif prop_name.startswith('filepath'):
            data[prop_name] = _realpath(prop)
        else:
            data[prop_name] = prop

    return data


def decode_image(data: dict[str, Any]) -> Image | None:
    if 'name' not in data:
        return None

    image = bpy.data.images.get(data['name'])
    size = data['resolution'] if 'resolution' in data else [1024, 1024]
    path = data['filepath_raw'] if 'filepath_raw' in data else ''

    if image is None or (path and path != _realpath(image.filepath)):
        if path and os.path.exists(path):
            image = bpy.data.images.load(path)
        else:
            image = bpy.data.images.new(
                data['name'], int(size[0]), int(size[1])
            )

        for prop_name in _IMAGE_PROPS:
            setattr(image, prop_name, data[prop_name])

    return image
