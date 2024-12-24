import random

from methods import *

def simple_calculation(id_exp, a12, a21, method_num, used_function=None):
    method = get_method(used_function, method_num, id_exp)
    a12_new, a21_new, _ = method.calculate(a12, a21)
    return a12_new, a21_new


def multi_start(id_exp: int, a12_min: float, a12_max: float, a21_min: float, a21_max: float, count: int, method_num: int, used_function=None):
    method = get_method(used_function, method_num, id_exp)
    result = []
    for i in range(count):
        a12 = random.uniform(a12_min, a12_max)
        a21 = random.uniform(a21_min, a21_max)
        a12_new, a21_new, _ = method.calculate(a12, a21)
        if a12_min <= a12_new <= a12_max and a21_min <= a21_new <= a21_max:
            result.append([a12_new, a21_new])
    return result


if __name__ == '__main__':
    #func = '8.31 * temp * x * (1 - x) * ((1 - x) * a1 + a2 * x) * 4 * x'
    func = functions.margulis
    result = simple_calculation(1, 0, 0, 1, func)
    print(result)