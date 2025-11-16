from bpy.props import EnumProperty, IntProperty, PointerProperty
from bpy.types import Material, Object, PropertyGroup


class ToonSettings(PropertyGroup):
    PROP_NAME = 'toon_settings'

    def _set_cast_shadows(self, value: int):
        self.id_data.pass_index = (
            (value << 12) | (self.id_data.pass_index & ~(7 << 12))
        )

    def _set_shadow_id(self, value: int):
        self.id_data.pass_index = (
            (value << 0) | (self.id_data.pass_index & ~(63 << 0))
        )

    def _set_transparent_id(self, value: int):
        self.id_data.pass_index = (
            (value << 6) | (self.id_data.pass_index & ~(63 << 6))
        )

    def _get_cast_shadows(self) -> int:
        return (self.id_data.pass_index >> 12) & 7

    def _get_shadow_id(self) -> int:
        return (self.id_data.pass_index >> 0) & 63

    def _get_transparent_id(self) -> int:
        return (self.id_data.pass_index >> 6) & 63

    shadow_casting_types = [
        ('0', 'Enable', ''),
        ('1', 'Only Front Surface', ''),
        ('2', 'Disable', '')
    ]

    cast_shadows: EnumProperty(
        name='Cast Shadows',
        default='0', items=shadow_casting_types,
        set=_set_cast_shadows, get=_get_cast_shadows
    )

    shadow_id: IntProperty(
        name='Shadow ID',
        default=0, min=0, max=63,
        set=_set_shadow_id, get=_get_shadow_id
    )

    transparent_id: IntProperty(
        name='Transparent ID',
        default=0, min=0, max=63,
        set=_set_transparent_id, get=_get_transparent_id
    )

    @staticmethod
    def register():
        setattr(
            Material, ToonSettings.PROP_NAME,
            PointerProperty(type=ToonSettings)
        )
        setattr(
            Object, ToonSettings.PROP_NAME,
            PointerProperty(type=ToonSettings)
        )

    @staticmethod
    def unregister():
        delattr(Material, ToonSettings.PROP_NAME)
        delattr(Object, ToonSettings.PROP_NAME)
