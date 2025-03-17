import re
import bpy
from .rules import ArmaturesRule


# Check not used customeshapes
class UnusedCustomShapeRules(ArmaturesRule):
    @classmethod
    def fix_armatures(cls, armatures):
        used = set()

        for a in armatures:
            for b in a.pose.bones:
                if b.custom_shape:
                    used.add(b.custom_shape.name)

        all = set()

        for o in bpy.data.objects:
            m = re.match(r'^[^_.]*_CUSTOMSHAPE.*$', o.name)

            if m:
                all.add(o.name)

        unused = all - used

        if unused:
            print(f'WARNING: Unused customshapes: {unused}')

            return False

        return True
