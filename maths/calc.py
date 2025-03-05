import random
from typing import *

from maths.methods import *

def simple_calculation(experiment_id: int, init_data: dict[str, float], method_num: int, used_function: Optional[str]=None):
    method = get_method(used_function, method_num, experiment_id)
    result, _ = method.calculate(init_data)
    return result


def multi_start(id_exp: int, a12_min: float, a12_max: float, a21_min: float, a21_max: float, count: int, method_num: int, used_function=None):
    method = get_method(used_function, method_num, id_exp)
    result = []
    for i in range(count):
        a12 = random.uniform(a12_min, a12_max)
        a21 = random.uniform(a21_min, a21_max)
        a12_new, a21_new, _ = method.calculate({'a12':a12, 'a21': a21})
        if a12_min <= a12_new <= a12_max and a21_min <= a21_new <= a21_max:
            result.append([a12_new, a21_new])
    return result
