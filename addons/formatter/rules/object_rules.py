import re
import bpy
from .rules import Report, ObjectRule


# Check not used customeshapes
class UnusedCustomShapesRule(ObjectRule):
    @classmethod
    def fix_object(cls, obj, **kwargs):
        if not re.match(r'^[^_.]*_CUSTOMSHAPE.*$', obj.name):
            return Report.nothing()

        for o in cls.local_objects():
            if o.type == 'ARMATURE':
                for b in o.pose.bones:
                    shape = b.custom_shape

                    if shape and shape.name == obj.name:
                        return Report.nothing()

        return Report.error(f'Unused customshapes: {obj.name}')
