from toon.utils import override

import bpy

from bpy.app.handlers import load_post, persistent
from bpy.types import ShaderNodeTexImage

from toon.props import Palette
from toon.props.base import EntryBase

from .manager import PaletteManager

_msgbus_owner = object()


class ManagablePalette(Palette):
    @override
    def parent(self) -> tuple[list[str], list[EntryBase]]:
        manager = PaletteManager.instance()
        names, entries = [], []

        for palette in manager.palettes():
            names.append(palette.name)
            entries.append(palette)

        return names, entries

    """
    Blender versions below 5.0.0 have a bug that prevents a PropertyGroup from
    storing an Image PointerProperty inside a NodeTree. Because of this, the UI
    directly references the image property of ShaderNodeTexImage.

    The following process updates the value of TextureUVSnapSize in PaletteEntity
    when the image property of a ShaderNodeTexImage is changed.
    """

    @staticmethod
    def _update_texture_uv_snap_size():
        manager = PaletteManager.instance()

        for palette in manager.palettes():
            for group in palette.entries:
                for entry in group.entries:
                    if entry.type != 'TEXTURE':
                        continue

                    image = entry.texture_image

                    if image is None:
                        continue

                    entry.texture_uv_snap_size = image.size

    @staticmethod
    @persistent
    def _subscribe_texture_update(dummy: str):
        bpy.msgbus.clear_by_owner(_msgbus_owner)
        bpy.msgbus.subscribe_rna(
            key=(ShaderNodeTexImage, 'image'),
            owner=_msgbus_owner,
            args=(),
            notify=ManagablePalette._update_texture_uv_snap_size
        )

    @classmethod
    def register(cls):
        super(ManagablePalette, cls).register()

        if ManagablePalette._subscribe_texture_update not in load_post:
            load_post.append(ManagablePalette._subscribe_texture_update)

    @staticmethod
    def unregister():
        if ManagablePalette._subscribe_texture_update in load_post:
            load_post.remove(ManagablePalette._subscribe_texture_update)
