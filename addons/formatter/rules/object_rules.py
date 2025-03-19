import re
import bpy
from .rules import ObjectRule


# Check not used customeshapes
class UnusedCustomShapeRule(ObjectRule):
    @classmethod
    def fix_object(cls, obj, **kwargs):
        if not re.match(r'^[^_.]*_CUSTOMSHAPE.*$', obj.name):
            return True

        for o in bpy.data.objects:
            if o.type == 'ARMATURE':
                for b in o.pose.bones:
                    shape = b.custom_shape

                    if shape and shape.name == obj.name:
                        return True

        print(f'WARNING: Unused customshapes: {obj.name}')

        return False
