from toon.utils import override

from bpy.props import BoolProperty, StringProperty
from bpy.types import Context, PropertyGroup

from .base import EntryBase, GroupBase
from .naming import make_unique_name


class Entry(EntryBase, PropertyGroup):
    def _parent_keys(self) -> list[str]:
        parent = self.parent()

        if parent is None:
            return []
        elif isinstance(parent, tuple):
            return parent[0]
        else:
            return parent.entries.keys()

    def _update_name(self, context: Context):
        if self.disable_update_name:
            return

        self.disable_update_name = True
        names = self._parent_keys()

        if names.count(self.name) > 1:
            self.name = make_unique_name(self.name, names)

        self.on_rename()
        self.disable_update_name = False

    disable_update_name: BoolProperty(default=False)

    name: StringProperty(update=_update_name)

    @override
    def parent(self) -> GroupBase | tuple[list[str], list[EntryBase]] | None:
        path = self.path_from_id().rsplit('.', 1)[0]

        return self.id_data.path_resolve(path)
