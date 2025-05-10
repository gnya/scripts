import re
from .rules import Report, MeshRule


# Check not used vertex groups
class UnusedVertexGroupsRule(MeshRule):
    @classmethod
    def fix_mesh(cls, mesh, **kwargs):
        bones = set()

        for m in mesh.modifiers:
            if m.type == 'ARMATURE' and m.object:
                for b in m.object.data.bones:
                    if b.use_deform:
                        bones.add(b.name)

        unused = []

        for vg in mesh.vertex_groups:
            if re.match('DEF_.*', vg.name):
                if vg.name not in bones:
                    unused.append(vg.name)

        if unused:
            r = Report.error(f'Unused vertex groups: {mesh.name}')
            r.description = f'vertex groups: {unused}'

            return r

        return Report.nothing()


# Check not used materials
class UnusedMaterialsRule(MeshRule):
    @classmethod
    def fix_mesh(cls, mesh, **kwargs):
        all = set(range(len(mesh.material_slots)))
        used = set()

        for p in mesh.data.polygons:
            used.add(p.material_index)

        if all - used:
            return Report.error(f'Unused materials: {mesh.name}')

        return Report.nothing()
