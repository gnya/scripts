from toon.utils import override

from bpy.types import NodeTree

from toon.props import Palette
from toon.props.base import EntryBase
from toon.utils import node_tree_update_post

from .manager import PaletteManager


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
    def _update_all_uv_snap_size(node_tree: NodeTree):
        manager = PaletteManager.instance()
        palette = manager.from_data(node_tree)

        if palette is None:
            return

        for group in palette.entries:
            for entry in group.entries:
                if entry.type != 'TEXTURE':
                    continue

                image = entry.texture_image

                if image is None:
                    continue

                entry.texture_uv_snap_size = image.size

    @classmethod
    def register(cls):
        super(ManagablePalette, cls).register()

        if cls._update_all_uv_snap_size not in node_tree_update_post:
            node_tree_update_post.append(cls._update_all_uv_snap_size)
