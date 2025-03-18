import re
import bpy
from .rules import ObjectRule


# Check not used customeshapes
class UnusedCustomShapeRules(ObjectRule):
    @classmethod
    def fix_object(cls, obj):
        m = re.match(r'^[^_.]*_CUSTOMSHAPE.*$', obj.name)

        if not m:
            return True

        for o in bpy.data.objects:
            if o.type == 'ARMATURE':
                for b in o.pose.bones:
                    shape = b.custom_shape

                    if shape and shape.name == obj.name:
                        return True

        print(f'WARNING: Unused customshapes: {obj.name}')

        return False
