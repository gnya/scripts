import re
from . import utils
from .rules import DataBoneRule


# Deform bone's name must start with "DEF"
class DefBoneNameRule(DataBoneRule):
    @classmethod
    def fix_data_bone(cls, bone, **kwargs):
        if re.match('DEF_.*', bone.name):
            if utils.reset_property(bone, 'use_deform', True):
                print(f'Change "{bone.name}" use_deform to True')

                return False
        else:
            if utils.reset_property(bone, 'use_deform', False):
                print(f'Change "{bone.name}" use_deform to False')

                return False

        return True
