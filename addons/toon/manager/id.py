from bpy.props import StringProperty
from bpy.types import PropertyGroup


class PaletteID(PropertyGroup):
    id_name: StringProperty()

    id_lib: StringProperty(default='')

    def id_key(self) -> str | tuple[str, str]:
        if not self.id_lib:
            return self.id_name
        else:
            return self.id_name, self.id_lib
