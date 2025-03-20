import re
from . import utils
from .rules import Report, ModifierRule


# Modifier's name rule
class ModifierNameRule(ModifierRule):
    @classmethod
    def fix_modifier(cls, modifier, **kwargs):
        modifier_names = {
            'MIRROR': 'Mirror',
            'SOLIDIFY': 'Solidify',
            'SURFACE_DEFORM': 'Surface Deform',
            'MASK': 'Mask',
            'DATA_TRANSFER': 'Data Transfer',
            'CAST': 'Cast',
            'LATTICE': 'Lattice',
            'SUBSURF': 'Subdivision',
            'HOOK': 'Hook',
            'ARMATURE': 'Armature',
            'NODES': 'Geometry Nodes'
        }

        if modifier.type not in modifier_names.keys():
            return Report.error(f'"{modifier.type}" is not supported')

        name = modifier_names[modifier.type]
        info = []

        if hasattr(modifier, 'object') and modifier.object:
            info.append(modifier.object.name)

        if hasattr(modifier, 'target') and modifier.target:
            info.append(modifier.target.name)

        if hasattr(modifier, 'subtarget') and modifier.subtarget:
            info.append(modifier.subtarget)

        if modifier.type == 'MASK':
            if hasattr(modifier, 'vertex_group') and modifier.vertex_group:
                info.append(modifier.vertex_group)

        if modifier.type == 'NODES':
            name = modifier.node_group.name

            keys = []
            items = []

            for i in modifier.node_group.inputs[1:]:
                keys.append(i.name.lower())

            for k, v in modifier.items():
                if re.match(r'^Input_\d*$', k):
                    items.append(v)

            for k, v in zip(keys, items):
                if k == 'target' and v:
                    info.append(v.name)

        suffix = ', '.join(info)

        if suffix:
            name += f' ({suffix})'

        if utils.reset_property(modifier, 'name', name):
            return Report.log(f'Rename to "{name}"')

        return Report.nothing()


class ModifierPanelRule(ModifierRule):
    @classmethod
    def fix_modifier(cls, modifier, **kwargs):
        if utils.reset_property(modifier, 'show_expanded', False):
            return Report.log(f'Shrink "{modifier.name}" constraint panel')

        return Report.nothing()


class SubSurfUVSmoothRule(ModifierRule):
    @classmethod
    def fix_modifier(cls, modifier, **kwargs):
        if modifier.type == 'SUBSURF':
            if utils.reset_property(modifier, 'uv_smooth', 'PRESERVE_CORNERS'):
                return Report.log(f'Change {modifier.name} uv_smooth to PRESERVE_CORNERS')

        return Report.nothing()
