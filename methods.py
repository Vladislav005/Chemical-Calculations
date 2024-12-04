import abc
import matplotlib.pyplot as plt
import json
import math
import random
from abc import abstractmethod
import decimal as dc
import time

import reliase
import functions
from config import user_name
from functions import Function
from matplotlib.pyplot import figure


# абстрактный класс - метод для обобщения всех используемых методов
class Method(abc.ABC):
    def   __init__(self, id_exp: int, used_function: Function = None):
        self.id_exp = id_exp
        self.used_function = used_function
        self.experiment_data = reliase.get_experiment_as_id(id_exp)

    def margulis(self, a1, a2, x, temp):
        #return 8.31 * temp * x * (1 - x) * ((1 - x) * a1 + a2 * x)
        #return functions.margulis.result({'a1': a1, 'a2': a2, 'x': x, 'temp': temp})
        return Function.margulis(a1, a2, x, temp)

    def minimum(self, gej, a1, a2, x, temp):
        return (gej - self.margulis(a1,a2,x,temp)) ** 2

    def minimum_sum(self, arr, a1, a2):
        summ = 0
        #temp = arr[0][0]
        temp = self.experiment_data['temperature']
        for i in range(1, len(arr)):
            x = arr[i][0]
            gej = arr[i][1]
            summ += self.minimum(gej, a1, a2, x, temp)
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


    def draw_chart(self, ax):
        arr = self.make_list(self.id_exp)

        a1, a2 = 0, 0

        otz = self.calculate(arr, a1, a2)
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
    def __init__(self, id_exp):
        super().__init__(id_exp)

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

    def calculate(self, list_of_values, a_1, a_2):
        a1 = a_1
        a2 = a_2
        iterations = 1
        minimorum = self.minimum_sum(list_of_values, a1, a2)
        for iterations in range(1, 100000):
            t = self.temperature(iterations)
            a1_new = self.neighbour(a1, t)
            a2_new = self.neighbour(a2, t)
            minimorum = self.minimum_sum(list_of_values, a1, a2)
            minimorum_new = self.minimum_sum(list_of_values, a1_new, a2_new)
            if self.P(minimorum, minimorum_new, t) >= random.random():
                a1 = a1_new
                a2 = a2_new

        return a1, a2, minimorum, iterations


# метод Гаусса - Зейделя
class MethodGaussZeidel(Method):
    def __init__(self, id_exp):
        super().__init__(id_exp)

    def calculate(self, list_of_values, a12, a21):
        a12 = a12
        a21 = a21
        a1 = a12
        a2 = a21
        step_a1 = 1
        step_a2 = 1
        iterations = 0
        minimorum = self.minimum_sum(list_of_values, a1, a2)
        a1_list = []
        a2_list = []
        while True:
            #print(str(self.minimum_sum(list_of_values, a1, a2)).replace('.', ','))
            if step_a1 <= 0.00001 or step_a2 <= 0.00001:
                break
            if self.minimum_sum(list_of_values, a1 + step_a1, a2) < minimorum:
                iterations += 1
                minimorum = self.minimum_sum(list_of_values, a1 + step_a1, a2)
                a1 += step_a1
                a1_list.append(str(a1).replace('.', ','))
                a2_list.append(str(a2).replace('.', ','))
            elif self.minimum_sum(list_of_values, a1 - step_a1, a2) < minimorum:
                iterations += 1
                minimorum = self.minimum_sum(list_of_values, a1 - step_a1, a2)
                a1 -= step_a1
                a1_list.append(str(a1).replace('.', ','))
                a2_list.append(str(a2).replace('.', ','))
            else:
                iterations += 1
                step_a1 /= 2
            if self.minimum_sum(list_of_values, a1, a2 + step_a2) < minimorum:
                iterations += 1
                minimorum = self.minimum_sum(list_of_values, a1, a2 + step_a2)
                a2 += step_a2
                a1_list.append(str(a1).replace('.', ','))
                a2_list.append(str(a2).replace('.', ','))
            elif self.minimum_sum(list_of_values, a1, a2 - step_a2) < minimorum:
                iterations += 1
                minimorum = self.minimum_sum(list_of_values, a1, a2 - step_a2)
                a2 -= step_a2
                a1_list.append(str(a1).replace('.', ','))
                a2_list.append(str(a2).replace('.', ','))
            else:
                step_a2 /= 2
        return a1, a2, minimorum, iterations

# метод Хукка - Дживса
class MethodHookJeeves(Method):
    def __init__(self, id):
        super().__init__(id)

    def calculate(self, mas_list, a12, a21):
        x_coord = [a12, a21]
        ans_list2 = []
        iterat = 0
        e = 0.0000001  # параметр окончания поиска
        step1 = 1
        step2 = 1
        xb_coord = x_coord[:]
        funct_b = self.minimum_sum(mas_list, xb_coord[0], xb_coord[1])
        while (step1 > e) or (step2 > e):
            iterat += 1
            x_coord = xb_coord[:]
            funct = funct_b
            x1_coord = x_coord[:]
            for i in range(2):
                # iterat += 1
                x1_coord[i] = x_coord[i] + (step1 if i == 0 else step2)
                funct1 = self.minimum_sum(mas_list, x1_coord[0], x1_coord[1])
                if funct1 < funct:
                    x_coord = x1_coord[:]
                    funct = funct1
                else:
                    x1_coord[i] = x_coord[i] - 2 * (step1 if i == 0 else step2)
                    funct1 = self.minimum_sum(mas_list, x1_coord[0], x1_coord[1])
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
                    funct = self.minimum_sum(mas_list, x_coord[0], x_coord[1])
                    x1_coord = x_coord[:]
                    for i in range(2):
                        x1_coord[i] = x_coord[i] + (step1 if i == 0 else step2)
                        funct1 = self.minimum_sum(mas_list, x1_coord[0], x1_coord[1])
                        if funct1 < funct:
                            x_coord = x1_coord[:]
                            funct = funct1
                        else:
                            x1_coord[i] = x_coord[i] - 2 * (step1 if i == 0 else step2)
                            funct1 = self.minimum_sum(mas_list, x1_coord[0], x1_coord[1])
                            if funct1 < funct:
                                x_coord = x1_coord[:]
                                funct = funct1
                    if funct >= funct_b:
                        break
            else:
                ans_list2.append(str(xb_coord[1]).replace('.', ','))
                step1 /= 2
                step2 /= 2
        return xb_coord[0], xb_coord[1], self.minimum_sum(mas_list, xb_coord[0], xb_coord[1]), iterat


# метод антиградиента
class MethodAntigradient(Method):
    D = dc.Decimal
    data = []
    T = D(0.0)
    R = D(8.31)

    def __init__(self, id_exp):
        super().__init__(id_exp)

    def f(self, x, y):
        x, y = D(x), D(y)
        fsm = D(0.0)
        for i in range(0, 10):
            G = D(data[i][1])
            x2 = D(data[i][0])
            x1 = D(1 - x2)
            fsm += D((G - R * T * x1 * x2 * (x * x1 + y * x2)) ** 2)
        return fsm

    def df_dx(self, x, y):
        x, y = D(x), D(y)
        derivative = D(0.0)
        for i in range(0, 10):
            G = D(data[i][1])
            x2 = D(data[i][0])
            x1 = D(1 - x2)
            derivative += D((G - R * T * x1 * x2 * (x * x1 + y * x2)) * (-2) * R * T * (x1 ** 2) * x2)
        return D(derivative)

    def df_dy(self,x, y):
        x, y = D(x), D(y)
        derivative = D(0.0)
        for i in range(0, 10):
            G = D(data[i][1])
            x2 = D(data[i][0])
            x1 = D(1 - x2)
            derivative += D((G - R * T * x1 * x2 * (x * x1 + y * x2)) * (-2) * R * T * x1 * (x2 ** 2))
        return D(derivative)

    def df2_dx(self,x, y):
        x, y = D(x), D(y)
        derivative2 = D(0.0)
        for i in range(0, 10):
            G = D(data[i][1])
            x2 = D(data[i][0])
            x1 = D(1 - x2)
            derivative2 += D(2 * (R ** 2) * (T ** 2) * (x1 ** 4) * (x2 ** 2))
        return D(derivative2)

    def df2_dy(self, x, y):
        x, y = D(x), D(y)
        derivative2 = D(0.0)
        for i in range(0, 10):
            G = D(data[i][1])
            x2 = D(data[i][0])
            x1 = D(1 - x2)
            derivative2 += D(2 * (R ** 2) * (T ** 2) * (x1 ** 2) * (x2 ** 4))
        return D(derivative2)

    def gradient(self, x0, y0):
        x0, y0 = D(x0), D(y0)
        cnt = 0
        eps = D(10 ** (-6))
        xn, yn = x0, y0
        lam = D(10 ** (-6))
        lam2 = D(10 ** (-7))
        while (cnt == 0) or (abs(f(x0, y0) - f(xn, yn)) > eps):
            cnt += 1
            yx = D(D(0.7) * df_dx(x0, y0))
            yy = D(D(0.8) * df_dy(x0, y0))
            x0, y0 = xn, yn
            xn = D(x0 - yx * lam - lam * df_dx(x0, y0))
            yn = D(y0 - yy * lam2 - lam2 * df_dy(x0, y0))
        return [f(xn, yn), xn, yn, cnt]

    def gradient2(self, x0, y0):
        x0, y0 = D(x0), D(y0)
        cnt = 0
        eps = D(10 ** (-6))
        xn, yn = x0, y0
        lam = D(10 ** (-5))
        lam2 = D(10 ** (-5))
        while (cnt == 0) or (abs(f(x0, y0) - f(xn, yn)) > eps):
            cnt += 1
            if f(xn, yn) > f(x0, y0):
                lam /= 2
                lam2 /= 2
            x0, y0 = xn, yn
            xn = D(x0 - lam * df_dx(x0, y0))
            yn = D(y0 - lam2 * df_dy(x0, y0))
        return [f(xn, yn), xn, yn, cnt]

    def df2_dxdy(self, x, y):
        x, y = D(x), D(y)
        derivative2 = D(0.0)
        for i in range(0, 10):
            G = D(data[i][1])
            x2 = D(data[i][0])
            x1 = D(1 - x2)
            derivative2 += D(2 * (R ** 2) * (T ** 2) * (x1 ** 3) * (x2 ** 3))
        return D(derivative2)

    def H(self, x, y):
        H = [[D(df2_dx(x, y)), D(df2_dxdy(x, y))],
             [D(df2_dxdy(x, y)), D(df2_dx(x, y))]]
        detH = D(H[0][0] * H[1][1] - H[0][1] * H[1][0])
        return [[H[1][1] / detH, (D(-1) * H[0][1]) / detH], [(D(-1) * H[1][0]) / detH, H[0][0] / detH]]

    def newton(self, x0, y0):
        x0, y0 = D(x0), D(y0)
        cnt = 0
        eps = D(10 ** (-6))
        xn, yn = x0, y0
        while (cnt == 0) or (abs(x0 - xn) > eps and abs(y0 - yn)):
            print(str(f(x0, y0)).replace('.', ','))
            cnt += 1
            x0, y0 = xn, yn
            InvH = H(x0, y0)
            xn = D(x0 - (df_dx(x0, y0) * InvH[0][0] + df_dy(x0, y0) * InvH[0][1]))
            yn = D(y0 - (df_dx(x0, y0) * InvH[1][0] + df_dy(x0, y0) * InvH[1][1]))
        return [f(xn, yn), xn, yn, cnt]


    def calculate(self, arr, a1, a2):
        infile = open(input())
        T = D(infile.readline())
        for i in range(10):
            data.append(list(map(float, infile.readline().split())))
        dat_mas = [[0, 0], [-1, 0], [-6, 3], [4, -35], [0, -203], [665, 789], [-805, -4673], [37638, -32048]]
        A12, A21 = 10 ** 3, -10 ** 3
        # x0, y0 = D(input('Start x: ')), D(input('Start y: '))
        t1 = time.perf_counter()
        # ans_list = newton(A12, A21)
        ans_list = newton(A12, A21)

        print(str(time.perf_counter() - t1).replace('.', ',')[:9])


if __name__ == '__main__':
    method = MethodGaussZeidel(1)
    a12, a21, minimum, _ = method.calculate(method.make_list(1), 0, 0)
    print(a12,a21,minimum)