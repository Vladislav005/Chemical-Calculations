import decimal as dc
from sympy import *

class Function:
    def __init__(self, function_string = ''):
        self.function_string = function_string
        self.request = f'res = {self.function_string}'
        self.compile_code = compile(self.request, '<string>', 'exec')

    def get_string(self):
        return self.function_string

    def result(self, initial_params = {}):
        ldict = initial_params
        exec(self.compile_code, globals(), ldict)
        return ldict['res']

    @staticmethod
    def margulis(a1, a2, x, temp):
        D = dc.Decimal
        return D(D(8.31) * D(temp) * D(x) * (1 - D(x)) * ((1 - D(x)) * D(a1) + D(a2) * D(x)))

margulis = Function("8.31 * temp * x * (1 - x) * ((1 - x) * a1 + a2 * x)")


if __name__ == '__main__':
    x = Symbol('x')
    a = Symbol('a')
    y = x ** 2 + 1 + x * a ** 2
    dy_dx = y.diff(x)
    print(dy_dx)
    f = lambdify([x,a],dy_dx)
    print(f(2,3))