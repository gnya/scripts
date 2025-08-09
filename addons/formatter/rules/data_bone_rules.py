import bpy
import re
from . import utils
from .rules import Report, DataBoneRule


# Deform bone's name must start with "DEF"
class DefBoneNameRule(DataBoneRule):
    @classmethod
    def fix_data_bone(cls, bone, **kwargs):
        if re.match('DEF_.*', bone.name):
            if utils.reset_property(bone, 'use_deform', True):
                return Report.log(f'Change "{bone.name}" use_deform to True')
        else:
            if utils.reset_property(bone, 'use_deform', False):
                return Report.log(f'Change "{bone.name}" use_deform to False')

        return Report.nothing()


# Check not used bone customeshapes
class UnusedBonesRule(DataBoneRule):
    @classmethod
    def fix_data_bone(cls, bone, **kwargs):
        if bone.children:
            return Report.nothing()

        if bone.name not in kwargs['used_bones']:
            return Report.error(f'Unused bones: {bone.name}')

        return Report.nothing()

    @classmethod
    def fix_armature(cls, armature, **kwargs):
        used_bones = set()

        for o in cls.local_objects():
            used_bones |= utils.bones_used_in_object(o, armature)

        return super().fix_armature(armature, used_bones=used_bones, **kwargs)
