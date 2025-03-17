import re
from .rules import DataBoneRule


# Deform bone's name must start with "DEF"
class DefBoneNameRule(DataBoneRule):
    @classmethod
    def fix_data_bone(cls, _, bone):
        if bone.use_deform:
            if not re.match('DEF_.*', bone.name):
                print(f'Change "{bone.name}" use_deform to False')
                bone.use_deform = False

                return False

        return True


# B-Bone's name rule
class BBoneNameRule(DataBoneRule):
    @classmethod
    def fix_data_bone(cls, armature, bone):
        if bone.bbone_segments > 1:
            m = re.match(r'DEF_.*(_b)\b.*', bone.name)

            if m:
                s = m.span(1)
                name = bone.name[:s[0]] + bone.name[s[1]:]
                print(f'Rename "{bone.name}" to "{name}"')

                if name not in armature.data.bones:
                    bone.name = name
                else:
                    print(f'WARNING: Can\'t rename "{bone.name}" to "{name}"')

                return False

        return True
