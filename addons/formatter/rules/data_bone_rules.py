import re
from .rules import DataBoneRule


# Deform bone's name must start with "DEF"
class DefBoneNameRule(DataBoneRule):
    @classmethod
    def fix_data_bone(cls, bone, **kwargs):
        if re.match('DEF_.*', bone.name):
            if not bone.use_deform:
                print(f'Change "{bone.name}" use_deform to True')
                bone.use_deform = True

                return False
        else:
            if bone.use_deform:
                print(f'Change "{bone.name}" use_deform to False')
                bone.use_deform = False

                return False

        return True
