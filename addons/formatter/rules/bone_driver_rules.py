import re
from . import utils
from .rules import BoneDriverRule


# Check bone driver is symmetrical
class SymmetryBoneDriverRule(BoneDriverRule):
    @classmethod
    def fix_bone_driver(cls, drivers, driver):
        index = driver.array_index
        path = driver.data_path
        m = re.match(r'pose\.bones\["([^\]]*)"\]', path)

        if m:
            mirror_path = utils.switch_lr(path)
            mirror_driver = drivers.find(mirror_path, index=index)

            if not mirror_driver:
                print(f'WARNING: "{path}" doesn\'t have pair driver')

                return False

            variables = driver.driver.variables
            mirror_variables = mirror_driver.driver.variables

            for v in variables:
                mirror_v = mirror_variables.get(utils.switch_lr(v.name))

                if not mirror_v:
                    print(f'WARNING: "{path}" doesn\'t have pair variable')

                    return False

                is_mirror, s = utils.is_symmetrical_driver_variable(v, mirror_v)

                if not is_mirror:
                    print(f'WARNING: "{path}" doesn\'t have pair variable: {s}')

                    return False

        return True
