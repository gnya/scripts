import re
from . import utils
from .rules import BoneDriverRule


# Check bone driver is symmetrical
class SymmetryBoneDriverRule(BoneDriverRule):
    @classmethod
    def fix_bone_driver(cls, driver, **kwargs):
        index = driver.array_index
        path = driver.data_path
        m = re.match(r'pose\.bones\["([^\]]*)"\]', path)

        if m:
            drivers = kwargs['drivers']
            pair_path = utils.switch_lr(path)
            pair_driver = drivers.find(pair_path, index=index)

            if not pair_driver:
                print(f'WARNING: "{path}" doesn\'t have pair driver')

                return False

            variables = driver.driver.variables
            pair_variables = pair_driver.driver.variables

            for v in variables:
                pair_v = pair_variables.get(utils.switch_lr(v.name))

                if not pair_v:
                    print(f'WARNING: "{path}" doesn\'t have pair variable')

                    return False

                is_pair, s = utils.is_symmetrical_driver_variable(v, pair_v)

                if not is_pair:
                    print(f'WARNING: "{path}" doesn\'t have pair variable: {s}')

                    return False

        return True
