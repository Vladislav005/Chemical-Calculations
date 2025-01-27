import abc
import matplotlib.pyplot as plt
import json
import math
import random
from abc import abstractmethod
import decimal as dc

import reliase
import functions
from config import user_name
from functions import Function
from matplotlib.pyplot import figure


D = dc.Decimal
R = D(8.31)

# абстрактный класс - метод для обобщения всех используемых методов
class Method(abc.ABC):
    def __init__(self, id_exp: int, used_function: Function):
        self.id_exp = id_exp
        self.used_function = used_function
        self.experiment_data = reliase.get_experiment_as_id(id_exp)
        self.data = self.make_list(self.id_exp)
        self.temp = D(self.experiment_data['temperature'])
    
    def model_result(self, intial_params: dict):
        return D(self.used_function.result(intial_params))

    def margulis(self, a1, a2, x, temp):
        return R * D(temp) * D(x) * (1 - D(x)) * ((1 - D(x)) * D(a1) + D(a2) * D(x))

    def minimum(self, gej, a1, a2, x, temp):
        return (gej - self.model_result({'a1': float(a1), 'a2': float(a2), 'x': float(x), 'temp': float(temp)})) ** 2
        #return (gej - self.margulis(a1, a2, x, temp)) ** 2

    def minimum_sum(self, arr, a1, a2):
        summ = 0
        #temp = arr[0][0]
        for i in range(1, len(arr)):
            x = arr[i][0]
            gej = arr[i][1]
            summ += self.minimum(gej, a1, a2, x, self.temp)
        return summ

    @abstractmethod
    def calculate(self, arr, a1, a2): pass

    @staticmethod
    def make_list(id_exp):
        experiment = reliase.get_experiment_as_id(id_exp)
        source_data = json.loads(experiment['source_data'])
        result = []
        for i in range(min(len(source_data['x2']), len(source_data['GEJ']))):
            result.append([float(source_data['x2'][i]), int(source_data['GEJ'][i])])
        return result
    
    def f(self, x, y):
        x, y = D(x), D(y)
        fsm = D(0.0)
        for i in range(0, 10):
            G = D(self.data[i][1])
            x2 = D(self.data[i][0])
            x1 = D(1 - x2)
            fsm += D((G - R * self.temp * x1 * x2 * (x * x1 + y * x2)) ** 2)
        return fsm

    def df_dx(self, x, y):
        x, y = D(x), D(y)
        derivative = D(0.0)
        for i in range(0, 10):
            G = D(self.data[i][1])
            x2 = D(self.data[i][0])
            x1 = D(1 - x2)
            derivative += D((G - R * self.temp * x1 * x2 * (x * x1 + y * x2)) * (-2) * R * self.temp * (x1 ** 2) * x2)
        return D(derivative)

    def df_dy(self,x, y):
        x, y = D(x), D(y)
        derivative = D(0.0)
        for i in range(0, 10):
            G = D(self.data[i][1])
            x2 = D(self.data[i][0])
            x1 = D(1 - x2)
            derivative += D((G - R * self.temp * x1 * x2 * (x * x1 + y * x2)) * (-2) * R * self.temp * x1 * (x2 ** 2))
        return D(derivative)

    def df2_dx(self,x, y):
        x, y = D(x), D(y)
        derivative2 = D(0.0)
        for i in range(0, 10):
            G = D(self.data[i][1])
            x2 = D(self.data[i][0])
            x1 = D(1 - x2)
            derivative2 += D(2 * (R ** 2) * (self.temp ** 2) * (x1 ** 4) * (x2 ** 2))
        return D(derivative2)

    def df2_dy(self, x, y):
        x, y = D(x), D(y)
        derivative2 = D(0.0)
        for i in range(0, 10):
            G = D(self.data[i][1])
            x2 = D(self.data[i][0])
            x1 = D(1 - x2)
            derivative2 += D(2 * (R ** 2) * (self.temp ** 2) * (x1 ** 2) * (x2 ** 4))
        return D(derivative2)

    def df2_dxdy(self, x, y):
        x, y = D(x), D(y)
        derivative2 = D(0.0)
        for i in range(0, 10):
            G = D(self.data[i][1])
            x2 = D(self.data[i][0])
            x1 = D(1 - x2)
            derivative2 += D(2 * (R ** 2) * (self.temp ** 2) * (x1 ** 3) * (x2 ** 3))
        return D(derivative2)

    def H(self, x, y):
        H = [[D(self.df2_dx(x, y)), D(self.df2_dxdy(x, y))],
             [D(self.df2_dxdy(x, y)), D(self.df2_dx(x, y))]]
        detH = D(H[0][0] * H[1][1] - H[0][1] * H[1][0])
        return [[H[1][1] / detH, (D(-1) * H[0][1]) / detH], [(D(-1) * H[1][0]) / detH, H[0][0] / detH]]


    def draw_chart(self, ax=None):
        arr = self.make_list(self.id_exp)
        a1, a2 = 0, 0

        otz = self.calculate(a1, a2)
        a12 = otz[0]
        a21 = otz[1]

        t = reliase.get_experiment_as_id(self.id_exp)['temperature']
        x = []
        i = arr[0][0]
        while i < arr[len(arr) - 1][0]:
            x.append(i)
            i += 0.005
        x = [0] + x + [1]
        y = [self.margulis(a12, a21, x2, t) for x2 in x]

        x2 = [arr[i][0] for i in range(len(arr))]
        x2 = [0] + x2 + [1]
        y2 = [self.margulis(a12, a21, x_2, t) for x_2 in x2]

        plt.plot(x, y)
        plt.xlabel('x2')  # Подпись для оси х
        plt.ylabel('margulis')  # Подпись для оси y
        plt.title('T = ' + str(t))  # Название
        plt.plot(x, y, color='green', marker='o', markersize=0.01)
        plt.plot(x2, y2, color='red', marker='o', markersize=7, linestyle='')
        plt.grid()
        #plt.show()
        ax = plt



# метод имитации отжига
class MethodOfSimulatedAnnealing(Method):
    def __init__(self, id_exp: int, used_function: Function = None):
        super().__init__(id_exp, used_function)

    @staticmethod
    def temperature(k):
        return 10 / math.log(1 + k)

    @staticmethod
    def neighbour(a, t):
        return a + (random.random() * t - t / 2)

    @staticmethod
    def P(old, new, t):
        ans = 0
        try:
            ans = math.exp(new - old)
        except OverflowError:
            ans = float('inf')
        return 1 / (1 + ans / t)

    def calculate(self, a_1, a_2):
        a1 = a_1
        a2 = a_2
        iterations = 1
        minimorum = self.minimum_sum(self.data, a1, a2)
        for iterations in range(1, 100000):
            t = self.temperature(iterations)
            a1_new = self.neighbour(a1, t)
            a2_new = self.neighbour(a2, t)
            minimorum = self.minimum_sum(self.data, a1, a2)
            minimorum_new = self.minimum_sum(self.data, a1_new, a2_new)
            if self.P(minimorum, minimorum_new, t) >= random.random():
                a1 = a1_new
                a2 = a2_new

        return round(a1, 5), round(a2, 5), round(minimorum, 5)

# метод Гаусса - Зейделя
class MethodGaussZeidel(Method):
    def __init__(self, id_exp: int, used_function: Function = None):
        super().__init__(id_exp, used_function)

    def calculate(self, a12, a21):
        a12 = a12
        a21 = a21
        a1 = a12
        a2 = a21
        step_a1 = 1
        step_a2 = 1
        iterations = 0
        minimorum = self.minimum_sum(self.data, a1, a2)
        a1_list = []
        a2_list = []
        while True:
            #print(str(self.minimum_sum(self.data, a1, a2)).replace('.', ','))
            if step_a1 <= 0.00001 or step_a2 <= 0.00001:
                break
            if self.minimum_sum(self.data, a1 + step_a1, a2) < minimorum:
                iterations += 1
                minimorum = self.minimum_sum(self.data, a1 + step_a1, a2)
                a1 += step_a1
                a1_list.append(str(a1).replace('.', ','))
                a2_list.append(str(a2).replace('.', ','))
            elif self.minimum_sum(self.data, a1 - step_a1, a2) < minimorum:
                iterations += 1
                minimorum = self.minimum_sum(self.data, a1 - step_a1, a2)
                a1 -= step_a1
                a1_list.append(str(a1).replace('.', ','))
                a2_list.append(str(a2).replace('.', ','))
            else:
                iterations += 1
                step_a1 /= 2
            if self.minimum_sum(self.data, a1, a2 + step_a2) < minimorum:
                iterations += 1
                minimorum = self.minimum_sum(self.data, a1, a2 + step_a2)
                a2 += step_a2
                a1_list.append(str(a1).replace('.', ','))
                a2_list.append(str(a2).replace('.', ','))
            elif self.minimum_sum(self.data, a1, a2 - step_a2) < minimorum:
                iterations += 1
                minimorum = self.minimum_sum(self.data, a1, a2 - step_a2)
                a2 -= step_a2
                a1_list.append(str(a1).replace('.', ','))
                a2_list.append(str(a2).replace('.', ','))
            else:
                step_a2 /= 2
        return round(a1, 5), round(a2, 5), round(minimorum, 5)

# метод Хукка - Дживса
class MethodHookJeeves(Method):
    def __init__(self, id_exp: int, used_function: Function = None):
        super().__init__(id_exp, used_function)

    def calculate(self, a12, a21):
        x_coord = [a12, a21]
        ans_list2 = []
        iterat = 0
        e = 0.0000001  # параметр окончания поиска
        step1 = 1
        step2 = 1
        xb_coord = x_coord[:]
        funct_b = self.minimum_sum(self.data, xb_coord[0], xb_coord[1])
        while (step1 > e) or (step2 > e):
            iterat += 1
            x_coord = xb_coord[:]
            funct = funct_b
            x1_coord = x_coord[:]
            for i in range(2):
                # iterat += 1
                x1_coord[i] = x_coord[i] + (step1 if i == 0 else step2)
                funct1 = self.minimum_sum(self.data, x1_coord[0], x1_coord[1])
                if funct1 < funct:
                    x_coord = x1_coord[:]
                    funct = funct1
                else:
                    x1_coord[i] = x_coord[i] - 2 * (step1 if i == 0 else step2)
                    funct1 = self.minimum_sum(self.data, x1_coord[0], x1_coord[1])
                    if funct1 < funct:
                        x_coord = x1_coord[:]
                        funct = funct1

            if funct < funct_b:
                while True:
                    # iterat += 1
                    xpb_coord = xb_coord[:]
                    xb_coord = x_coord[:]
                    funct_b = funct
                    ans_list2.append(str(xb_coord[1]).replace('.', ','))
                    xp_coord = [0, 0]
                    for i in range(len(xp_coord)):
                        xp_coord[i] = xpb_coord[i] + 2 * (xb_coord[i] - xpb_coord[i])

                    x_coord = xp_coord[:]
                    funct = self.minimum_sum(self.data, x_coord[0], x_coord[1])
                    x1_coord = x_coord[:]
                    for i in range(2):
                        x1_coord[i] = x_coord[i] + (step1 if i == 0 else step2)
                        funct1 = self.minimum_sum(self.data, x1_coord[0], x1_coord[1])
                        if funct1 < funct:
                            x_coord = x1_coord[:]
                            funct = funct1
                        else:
                            x1_coord[i] = x_coord[i] - 2 * (step1 if i == 0 else step2)
                            funct1 = self.minimum_sum(self.data, x1_coord[0], x1_coord[1])
                            if funct1 < funct:
                                x_coord = x1_coord[:]
                                funct = funct1
                    if funct >= funct_b:
                        break
            else:
                ans_list2.append(str(xb_coord[1]).replace('.', ','))
                step1 /= 2
                step2 /= 2
        return round(xb_coord[0], 5), round(xb_coord[1], 5), round(self.minimum_sum(self.data, xb_coord[0], xb_coord[1]), 5)

# метод антиградиента
class MethodAntigradient(Method):
    def __init__(self, id_exp: int, used_function: Function = None):
        super().__init__(id_exp, used_function)
    
    def calculate(self,x0, y0):
        x0, y0 = D(x0), D(y0)
        cnt = 0
        eps = D(10 ** (-6))
        xn, yn = x0, y0
        lam = D(10 ** (-5))
        lam2 = D(10 ** (-5))
        while (cnt == 0) or (abs(self.f(x0, y0) - self.f(xn, yn)) > eps):
            cnt += 1
            if self.f(xn, yn) > self.f(x0, y0):
                lam /= 2
                lam2 /= 2
            x0, y0 = xn, yn
            xn = D(x0 - lam * self.df_dx(x0, y0))
            yn = D(y0 - lam2 * self.df_dy(x0, y0))
        return round(xn, 5), round(yn, 5), round(self.f(xn, yn), 5)

# метод Ньютона
class MethodNewton(Method):
    def __init__(self, id_exp: int, used_function: Function = None):
        super().__init__(id_exp, used_function)
    
    def calculate(self, x0, y0):
        x0, y0 = D(x0), D(y0)
        cnt = 0
        eps = D(10 ** (-6))
        xn, yn = x0, y0
        while (cnt == 0) or (abs(x0 - xn) > eps and abs(y0 - yn)):
            cnt += 1
            x0, y0 = xn, yn
            InvH = self.H(x0, y0)
            xn = D(x0 - (self.df_dx(x0, y0) * InvH[0][0] + self.df_dy(x0, y0) * InvH[0][1]))
            yn = D(y0 - (self.df_dx(x0, y0) * InvH[1][0] + self.df_dy(x0, y0) * InvH[1][1]))
        return round(xn, 5), round(yn, 5), round(self.f(xn, yn), 5)


def get_method(used_function: Function = None, method_num: int = 0, id_exp: int = 0):
    method = None
    match method_num:
        case 0:
            method = MethodOfSimulatedAnnealing(id_exp, used_function)
        case 1:
            method = MethodGaussZeidel(id_exp, used_function)
        case 2:
            method = MethodHookJeeves(id_exp, used_function)
        case 3:
            method = MethodAntigradient(id_exp, used_function)
        case 4:
            method = MethodNewton(id_exp, used_function)
    return method


if __name__ == '__main__':
    method = MethodOfSimulatedAnnealing(1, functions.margulis)
    a12, a21, minimum = method.calculate(0, 0)
    print(a12,a21,minimum)

    method = MethodGaussZeidel(1, functions.margulis)
    a12, a21, minimum = method.calculate(0, 0)
    print(a12,a21,minimum)

    method = MethodHookJeeves(1, functions.margulis)
    a12, a21, minimum = method.calculate(0, 0)
    print(a12,a21,minimum)

    method = MethodAntigradient(1, functions.margulis)
    a12, a21, minimum = method.calculate(0, 0)
    print(a12,a21,minimum)
    method.draw_chart()

    method = MethodNewton(1, functions.margulis)
    a12, a21, minimum = method.calculate(0, 0)
    print(a12,a21,minimum)