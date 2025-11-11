from bpy.props import BoolProperty, StringProperty
from bpy.types import PropertyGroup

from toon.utils import override

from .base import EntryBase, GroupBase
from .naming import make_unique_name


class Entry(EntryBase, PropertyGroup):
    def _parent_keys(self):
        parent = self.parent()

        if parent is None:
            return []
        elif isinstance(parent, tuple):
            return parent[0]
        elif isinstance(parent, GroupBase):
            return parent.items.keys()

        return []

    def _update_name(self, context):
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
    def parent(self) -> GroupBase | dict[str, EntryBase] | None:
        path = self.path_from_id().rsplit('.', 1)[0]

        return self.id_data.path_resolve(path)
