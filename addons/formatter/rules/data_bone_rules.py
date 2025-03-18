import re
from .rules import DataBoneRule


# Deform bone's name must start with "DEF"
class DefBoneNameRule(DataBoneRule):
    @classmethod
    def fix_data_bone(cls, bone, **kwargs):
        if bone.use_deform:
            if not re.match('DEF_.*', bone.name):
                print(f'Change "{bone.name}" use_deform to False')
                bone.use_deform = False

                return False

        return True
