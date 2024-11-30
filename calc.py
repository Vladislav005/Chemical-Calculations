import random

from methods import MethodOfSimulatedAnnealing, MethodGaussZeidel, MethodHookJeeves, MethodAntigradient


def simple_calculation(id_exp, a12, a21, method_num):
    method = None
    match method_num:
        case 0:
            method = MethodOfSimulatedAnnealing(id_exp)
        case 1:
            method = MethodGaussZeidel(id_exp)
        case 2:
            method = MethodHookJeeves(id_exp)
        case 3:
            method = MethodAntigradient(id_exp)

    a12_new, a21_new, _, _ = method.calculate(method.make_list(id_exp), a12, a21)
    return a12_new, a21_new


def multi_start(id_exp: int, a12_min: float, a12_max: float, a21_min: float, a21_max: float, count: int, method_num: int):
    method = None
    match method_num:
        case 0:
            method = MethodOfSimulatedAnnealing(id_exp)
        case 1:
            method = MethodGaussZeidel(id_exp)
        case 2:
            method = MethodHookJeeves(id_exp)
        case 3:
            method = MethodAntigradient(id_exp)

    iteration = 0
    result = []
    while iteration < count:
        a12 = random.uniform(a12_min, a12_max)
        a21 = random.uniform(a21_min, a21_max)
        a12_new, a21_new, _, _ = method.calculate(method.make_list(id_exp), a12, a21)
        if a12_min <= a12_new <= a12_max and a21_min <= a21_new <= a21_max:
            result.append([a12_new, a21_new])
        iteration += 1
    return result


if __name__ == '__main__':
    result = multi_start(0,0,100000,0,100000,10,0)
    print(result)