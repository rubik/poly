import re
import copy
import operator
import functools
import fractions
import itertools


__all__ = ['monomial', 'parse', 'Poly']


def dict2poly(func):
    def wrapper(*args, **kwargs):
        d = func(*args, **kwargs)
        return sorted(zip(d.values(), d.keys()), key=lambda i: -i[1])
    return wrapper


def polyize(func):
    def wrapper(*args, **kwargs):
        return Poly(func(*args, **kwargs))
    return wrapper


def monomial(coeff=1, power=1):
    return Poly([(coeff, power)])


class Poly(object):

    _coeff_format = {
        1: '+',
        -1: '-'
    }

    _exp_format = {
        0: '',
        1: 'x',
    }

    def __init__(self, poly=[]):
        self.poly = self.simplify(poly)

    def __repr__(self):
        if not self.poly:
            return '0'
        return ' '.join(map(self._format_monomial, self.poly))

    def _format_monomial(self, m):
        c, p = m
        if c in self._coeff_format:
            coeff = self._coeff_format[c]
        else:
            coeff = str(c) if c < 0 else '+' + str(c)
        if p in self._exp_format:
            power = str(abs(c)) if c in (-1, 1) and p == 0 \
                    else self._exp_format[p]
        else:
            power = 'x^{0}'.format(p)
        return (coeff + power).replace('+', '+ ').replace('-', '- ')

    @staticmethod
    @dict2poly
    def simplify(poly):
        new_poly = {}
        if not poly:
            return new_poly
        for coeff, power in poly:
            if not coeff:
                continue
            if power in new_poly:
                if new_poly[power] + coeff == 0:
                    del new_poly[power]
                    continue
                new_poly[power] += coeff
                continue
            new_poly[power] = coeff
        return new_poly

    @classmethod
    @polyize
    @dict2poly
    def from_string(cls, string):
        '''
        Build a polynomial from a string. You can use ** or ^ to indicate
        exponentiation. Valid polynomials include:

            3x - 2
            x + 1
            4x**2 + x - 1
            -2x^3 + x**2 - x + 1
        '''

        monomial_re = re.compile(r'([-+]?\d*)(x?)\^?(\d*)')
        string = string.replace(' ', '').replace('**', '^')
        poly = {}
        signs = {'+': 1, '-': -1}
        for c, x, p in monomial_re.findall(string):
            if not any((c, x, p)):
                continue
            coeff = signs[c] if c in ('+', '-') else int(c or 1)
            power = int(p or 1) if x else 0
            # multiple monomials with the same degree
            if power in poly:
                poly[power] += coeff
                continue
            poly[power] = coeff
        return poly

    ## CONVENIENCE METHODS & PROPERTIES ##

    @property
    def degree(self):
        if not self:
            return 0
        return self.poly[0][1]

    @property
    def rhs(self):
        rhs = self.poly[-1]
        if rhs[1] == 0:
            return rhs[0]
        return 0

    def append(self, other):
        return Poly(self.poly + other.poly)

    def is_num(self):
        if not self:
            return True
        return len(self.poly) == 1 and self.poly[0][1] == 0

    ## OPERATORS ##

    def __copy__(self):
        return Poly(copy.copy(self.poly))

    def __deepcopy__(self, memo):
        return Poly(copy.deepcopy(self.poly, memo))

    def __nonzero__(self):
        return bool(self.poly)

    def __bool__(self):
        return bool(self.poly)

    def __len__(self):
        return len(self.poly)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return Poly(self.poly[item])
        return Poly([self.poly[item]])

    def __eq__(self, other):
        return self.poly == other.poly

    def __ne__(self, other):
        return self.poly != other.poly

    def __pos__(self):
        return self

    def __neg__(self):
        return Poly([(-1, 0)]) * self

    def __add__(self, other):
        return Poly(self.poly + other.poly)

    def __sub__(self, other):
        return Poly(self.poly + (-other).poly)

    def __mul__(self, other):
        monomial_pairs = itertools.product(self.poly, other.poly)
        return Poly((a[0] * b[0], a[1] + b[1]) for a, b in monomial_pairs)

    def __divmod__(self, other):
        def div(a, b):
            return Poly([(fractions.Fraction(a[0]) / b[0], a[1] - b[1])])

        A, B = copy.deepcopy(self), copy.deepcopy(other)
        Q = Poly()
        if A.degree < B.degree:
            raise ValueError('The polynomials are not divisible')
        while A.degree >= B.degree:
            if not A:
                return Q, Poly()
            if A.is_num() and B.is_num():
                return Q.append(div(A.poly[0], B.poly[0])), Poly()

            quotient = div(A.poly[0], B.poly[0])
            A = A[1:]
            Q = Q.append(quotient)
            if len(B) == 1:
                continue
            m = B[1:]
            A += -quotient * m
        return Q, A

    def __div__(self, other):
        return self.__divmod__(other)[0]

    def __mod__(self, other):
        return self.__divmod__(other)[1]

    def __pow__(self, exp):
        if exp < 0:
            return NotImplemented
        elif exp == 0:
            if not self:
                return NotImplemented
            return monomial(power=0)
        elif exp == 1:
            return copy.deepcopy(self)
        elif len(self) == 1:
            return Poly([(self.poly[0][0], self.poly[0][1] * exp)])
        return functools.reduce(operator.mul, itertools.repeat(self, exp))
