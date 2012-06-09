import copy
import unittest
from poly import Poly, monomial


def pass_to(func, convert=(True, True), star=False):
    def wrapper(meth):
        def inner(self):
            for value, expected in meth(self).items():
                if convert[0] and not star:
                    value = Poly(value)
                if convert[1]:
                    if isinstance(expected, tuple):
                        expected = tuple(map(Poly, expected))
                    else:
                        expected = Poly(expected)
                val = func(*map(Poly, value)) if star else func(value)
                self.assertEqual(val, expected)
        return inner
    return wrapper


class TestPypolFuncs(unittest.TestCase):

    def test_monomial(self):
        self.assertEqual(monomial(1, 1), Poly([(1, 1)]))
        self.assertEqual(monomial(-1, 0), Poly([(-1, 0)]))
        self.assertEqual(monomial(0, 0), Poly([]))
        self.assertEqual(monomial(1, 2), Poly([(1, 2)]))

    @pass_to(Poly.from_string, (False, True))
    def test_parse(self):
        return {
            '3x - 2': [(3, 1), (-2, 0)],
            'x + 1': [(1, 1), (1, 0)],
            '4x**2 + x - 1': [(4, 2), (1, 1), (-1, 0)],
            '-2x^3 + x**2 -x + 1': [(-2, 3), (1, 2), (-1, 1), (1, 0)],
            '- x ^ 3 + 2': [(-1, 3), (2, 0)],
            '4 x': [(4, 1)],
            '- 5 x ^ 3 + 1 - 4': [(-5, 3), (-3, 0)],
            '-x - x^2': [(-1, 2), (-1, 1)],
            'x + x - 3x': [(-1, 1)],
        }


class TestPypolPoly(unittest.TestCase):

    @pass_to(Poly.__repr__, (True, False))
    def test_repr(self):
        return {
            ((1, 2), (4, 1), (-2, 0)): '+ x^2 + 4x - 2',
            ((-3, 4), (-1, 2)): '- 3x^4 - x^2',
            ((-2, 2), (3, 1)): '- 2x^2 + 3x',
            ((2, 0),): '+ 2',
            ((1, 1),): '+ x',
            ((-1, 10),): '- x^10',
            (): '0',
            ((-1, 0),): '- 1'
        }

    @pass_to(Poly.degree.fget, (True, False))
    def test_degree(self):
        return {
            ((-3, 2), (4, 0)): 2,
            ((4, 3), (0, 5), (0, 7), (9, 2)): 3,
            ((-1, 0),): 0,
            ((3, 2), (4, 1)): 2,
            (): 0,
        }

    @pass_to(Poly.rhs.fget, (True, False))
    def test_rhs(self):
        return {
            ((-3, 4), (4, 2)): 0,
            ((-1, 0),): -1,
            ((9, 0), (-3, 2), (4, 2), (-5, 1)): 9,
            ((2, 2), (0, 0)): 0,
        }

    @pass_to(Poly.append, star=True)
    def test_append(self):
        return {
            (((2, 3), (-3, 4)), ((1, 4), (2, 2))): [(-2, 4), (2, 3), (2, 2)],
            (((-2, 3), (1, 2), (1, 1)), ((3, 2),)): [(-2, 3), (4, 2), (1, 1)],
            (((3, 1),), ((-5, 1),)): [(-2, 1)],
            (((4, 2), (-1, 1)), ()): [(4, 2), (-1, 1)],
        }

    @pass_to(Poly.is_num, (True, False))
    def test_is_num(self):
        return {
            ((-2, 0),): True,
            ((9, 9), (0, 4)): False,
            ((1, 1), (1, 0)): False,
            ((0, 0),): True,
        }

    @pass_to(Poly.simplify, (False, False))
    def test_simplify(self):
        return {
            ((1, 2), (3, 0), (-1, 0)): [(1, 2), (2, 0)],
            ((-3, 2), (-4, 2), (0, 4), (-2, 1)): [(-7, 2), (-2, 1)],
            ((0, 2),): [],
            ((4, 4), (-4, 4)): [],
            ((2, 1), (-8, 0)): [(2, 1), (-8, 0)]
        }

    @pass_to(copy.copy)
    def test_copy(self):
        return {
            ((1, 4), (-1, 0)): [(1, 4), (-1, 0)],
            ((-1, 2), (2, 3), (4, 1)): [(2, 3), (-1, 2), (4, 1)],
            ((3, 2),): [(3, 2)],
        }

    @pass_to(copy.deepcopy)
    def test_deepcopy(self):
        return {
            ((1, 4), (-1, 0)): [(1, 4), (-1, 0)],
            ((-1, 2), (2, 3), (4, 1)): [(2, 3), (-1, 2), (4, 1)],
            ((3, 2),): [(3, 2)],
        }

    def test_getitem(self):
        self.assertEqual(Poly([(1, 2), (-1, 0)])[0], Poly([(1, 2)]))
        self.assertEqual(Poly([(-3, 0), (4, 4)])[0], Poly([(4, 4)]))
        self.assertEqual(Poly([(1, 1), (2, 0), (3, 2)])[1:],
                         Poly([(1, 1), (2, 0)]))
        self.assertEqual(Poly([(-2, 3), (1, 2), (-1, 0)])[2:3],
                         Poly([(-1, 0)]))

    @pass_to(Poly.__nonzero__, (True, False))
    def test_nonzero(self):
        return {
            (): False,
            ((1, 0),): True,
            ((0, 0),): False,
            ((1, 1), (-3, 1), (4, 2)): True,
        }

    @pass_to(Poly.__bool__, (True, False))
    def test_nonzero(self):
        return {
            (): False,
            ((1, 0),): True,
            ((0, 0),): False,
            ((1, 1), (-3, 1), (4, 2)): True,
        }

    @pass_to(len, (True, False))
    def test_len(self):
        return {
            (): 0,
            ((0, 0),): 0,
            ((1, 0),): 1,
            ((1, 4), (-1, 4), (1, 1)): 1,
            ((3, 2), (4, 1)): 2,
            ((1, 4), (-1, 3), (1, 2), (-1, 1), (1, 0)): 5
        }

    @pass_to(Poly.__eq__, (True, False), True)
    def test_eq(self):
        return {
            (((1, 3), (-1, 2)), ((1, 3), (2, 2), (-3, 2))): True,
            (((1, 3), (4, 2)), ((1, 3), (-4, 2))): False,
            (((1, 0),), ((1, 0),)): True,
            ((), ()): True,
        }

    @pass_to(Poly.__ne__, (True, False), True)
    def test_ne(self):
        return {
            (((1, 3), (-1, 2)), ((1, 3), (2, 2), (-3, 2))): False,
            (((1, 3), (4, 2)), ((1, 3), (-4, 2))): True,
            (((1, 0),), ((1, 0),)): False,
            ((), ()): False,
        }

    @pass_to(Poly.__pos__)
    def test_pos(self):
        return {
            (): [],
            ((1, 0), (-1, 1)): [(1, 0), (-1, 1)],
            ((3, 2), (-3, 2), (4, 1)): [(4, 1)],
        }

    @pass_to(Poly.__neg__)
    def test_neg(self):
        return {
            ((1, 1),): [(-1, 1)],
            ((2, 4), (-3, 5)): [(3, 5), (-2, 4)],
            ((3, 1), (1, 1)): [(-4, 1)],
            ((1, 1),): [(-1, 1)],
        }

    @pass_to(Poly.__add__, star=True)
    def test_add(self):
        return {
            (((3, 2), (4, 1)), ((1, 2), (-1, 1))): [(4, 2), (3, 1)],
            (((1, 2), (3, 3)), ((2, 4), (-1, 3))): [(2, 4), (2, 3), (1, 2)],
            (((3, 3),), ((-3, 3),)): [],
            (((1, 1), (-2, 4)), ((3, 1), (2, 4))): [(4, 1)],
            ((), ((-3, 2),)): [(-3, 2)],
        }

    @pass_to(Poly.__sub__, star=True)
    def test_sub(self):
        return {
            (((3, 2), (4, 1)), ((1, 2), (-1, 1))): [(2, 2), (5, 1)],
            (((1, 2), (3, 3)), ((2, 4), (3, 3))): [(-2, 4), (1, 2)],
            (((3, 3),), ((-3, 3),)): [(6, 3)],
            (((1, 1), (-2, 4)), ((3, 1), (2, 4))): [(-4, 4), (-2, 1)],
            ((), ((-3, 2),)): [(3, 2)],
        }

    @pass_to(Poly.__mul__, star=True)
    def test_mul(self):
        return {
            (((1, 1), (-1, 0)), ((1, 1), (-1, 0))): [(1, 2), (-2, 1), (1, 0)],
            (((1, 0),), ((2, 3), (-1, 4))): [(-1, 4), (2, 3)],
            (((-1, 1),), ((2, 3), (-1, 4))): [(1, 5), (-2, 4)]
        }

    @pass_to(divmod, star=True)
    def test_divmod(self):
        return {
            (((3, 3), (-2, 2), (4, 1), (-3, 0)), ((1, 2), (3, 1), (3, 0))):
                ([(3, 1), (-11, 0)], [(28, 1), (30, 0)]),
            (((1, 3), (-2, 2), (1, 1), (-5, 0)), ((-1, 1), (1, 0))):
                ([(-1, 2), (1, 1)], [(-5, 0)]),
            (((1, 2), (8, 1), (-54, 0)), ((1, 1), (11, 0))):
                ([(1, 1), (-3, 0)], [(-21, 0)]),
            (((6, 0),), ((2, 0),)): ([(3, 0)], []),
            (((4, 2), (-2, 1), (2, 0)), ((2, 0),)):
                ([(2, 2), (-1, 1), (1, 0)], []),
            ((), ()): ([], []),
        }

    def test_divmod_value_error(self):
        self.assertRaises(ValueError, divmod,
                          Poly([(1, 2), (-3, 1)]), Poly([(3, 3), (4, 0)]))

    @pass_to(Poly.__div__, star=True)
    def test_div(self):
        return {
            (((3, 3), (-2, 2), (4, 1), (-3, 0)), ((1, 2), (3, 1), (3, 0))):
                [(3, 1), (-11, 0)],
            (((1, 3), (-2, 2), (1, 1), (-5, 0)), ((-1, 1), (1, 0))):
                [(-1, 2), (1, 1)],
            (((1, 2), (8, 1), (-54, 0)), ((1, 1), (11, 0))):
                [(1, 1), (-3, 0)],
            (((6, 0),), ((2, 0),)): [(3, 0)],
            (((4, 2), (-2, 1), (2, 0)), ((2, 0),)):
                [(2, 2), (-1, 1), (1, 0)],
            ((), ()): [],
        }

    @pass_to(Poly.__mod__, star=True)
    def test_mod(self):
        return {
            (((3, 3), (-2, 2), (4, 1), (-3, 0)), ((1, 2), (3, 1), (3, 0))):
                [(28, 1), (30, 0)],
            (((1, 3), (-2, 2), (1, 1), (-5, 0)), ((-1, 1), (1, 0))):
                [(-5, 0)],
            (((1, 2), (8, 1), (-54, 0)), ((1, 1), (11, 0))):
                [(-21, 0)],
            (((6, 0),), ((2, 0),)): [],
            (((4, 2), (-2, 1), (2, 0)), ((2, 0),)):
                [],
            ((), ()): [],
        }

    def test_pow(self):
        self.assertRaises(TypeError, lambda: Poly([(2, 2), (-1, 1)]) ** -1)
        self.assertRaises(TypeError, lambda: Poly([]) ** 0)
        self.assertEqual(Poly([(1, 3), (2, 1)]) ** 1, Poly([(1, 3), (2, 1)]))
        self.assertEqual(Poly([(1, 1), (-1, 0)]) ** 2,
                         Poly([(1, 2), (-2, 1), (1, 0)]))
        self.assertEqual(Poly([(1, 3), (-1, 2)]) ** 0, Poly([(1, 0)]))
        self.assertEqual(Poly([(1, 1)]) ** 3, Poly([(1, 3)]))
        self.assertEqual(Poly([(1, 4)]) ** 3, Poly([(1, 12)]))


if __name__ == '__main__':
    unittest.main()
