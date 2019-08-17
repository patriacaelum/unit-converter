import numpy as np
import unittest

from scalar import Scalar, ScalarError
from unit import Unit, UnitError


class TestScalar(unittest.TestCase):
    def test_init(self):
        # Integer value
        s = Scalar(2)

        self.assertEqual(s.values, 2)
        self.assertEqual(s.units, '')

        self.assertEqual(s.latex, '')
        self.assertEqual(s.parsed, [Unit('')])
        self.assertEqual(s.unparsed, '')

        # Float value
        s = Scalar(2.0)

        self.assertEqual(s.values, 2.0)
        self.assertEqual(s.units, '')

        self.assertEqual(s.latex, '')
        self.assertEqual(s.parsed, [Unit('')])
        self.assertEqual(s.unparsed, '')

        # Iterable value
        s = Scalar([1, 2, 3])

        self.assertListEqual(s.values.tolist(), [1, 2, 3])
        self.assertEqual(s.units, '')

        self.assertEqual(s.latex, '')
        self.assertEqual(s.parsed, [Unit('')])
        self.assertEqual(s.unparsed, '')

        # Single unit
        s = Scalar(2, 'kg^2')

        self.assertEqual(s.values, 2)
        self.assertEqual(s.units, 'kg^2')

        self.assertEqual(s.latex, 'kg^{2}')
        self.assertEqual(s.parsed, [Unit('kg^2')])
        self.assertEqual(s.unparsed, 'kg^2')

        # Multiple units
        s = Scalar(2, 'kg^2*m^3/A*s^4')

        self.assertEqual(s.values, 2)
        self.assertEqual(s.units, 'kg^2*m^3/A*s^4')

        self.assertEqual(s.latex, 'kg^{2}.m^{3}.A^{-1}.s^{-4}')
        self.assertEqual(
            s.parsed,
            [Unit('kg^2'), Unit('m^3'), Unit('A^-1'), Unit('s^-4')]
        )
        self.assertEqual(s.unparsed, 'kg^2*m^3/A*s^4')

        # Incorrect inputs
        with self.assertRaises(ScalarError):
            Scalar('a')

        with self.assertRaises(ScalarError):
            Scalar(2, 3)

    def test_base(self):
        # Standard SI unit
        s = Scalar(2, 'mm^2')

        self.assertTupleEqual(s.base(), ([Unit('m^2')], 1e-6))

        # Special case for "kg"
        s = Scalar(2, 'g^2')

        self.assertTupleEqual(s.base(), ([Unit('kg^2')], 1e-6))

        # Derived unit
        s = Scalar(2, 'kN^2')

        self.assertTupleEqual(s.base(), ([Unit('kg^2'), Unit('m^2'), Unit('s^-4')], 1e6))

        # Multiple units
        s = Scalar(2, 'kg*N^2/s^2')

        self.assertTupleEqual(
            s.base(),
            ([Unit('kg'), Unit('kg^2'), Unit('m^2'), Unit('s^-4'), Unit('s^-2')], 1e0)
        )

    def test_conversion_factor(self):
        s = Scalar(2)

        self.assertEqual(s.conversion_factor(Unit('mm'), Unit('m')), 1e-3)
        self.assertEqual(s.conversion_factor(Unit('kg^2'), Unit('mg^2')), 1e12)
        self.assertEqual(s.conversion_factor(Unit('s^-1'), Unit('ms^-1')), 1e-3)

        with self.assertRaises(ScalarError):
            s. conversion_factor(Unit('mm'), Unit('m^2'))

    def test_convert(self):
        # TODO: add temperature conversions and time conversions
        pass

    def test_convert_temperature(self):
        pass

    def test_is_temperature(self):
        pass

    def test_parse(self):
        s = Scalar(2)

        self.assertEqual(s.parse(''), [Unit('')])
        self.assertEqual(s.parse('kg^2'), [Unit('kg^2')])
        self.assertEqual(
            s.parse('kg^2*m^3/s^4'),
            [Unit('kg^2'), Unit('m^3'), Unit('s^-4')]
        )

    def test_simplify(self):
        s = Scalar(2)

        # Without converting to base units
        self.assertTupleEqual(
            s.simplify(s.parse('mm^2')),
            ([Unit('mm^2')], 1e0)
        )
        self.assertTupleEqual(
            s.simplify(s.parse('kg*m/m')),
            ([Unit('kg')], 1e0)
        )
        self.assertTupleEqual(
            s.simplify(s.parse('kg*m^3/m')),
            ([Unit('kg'), Unit('m^2')], 1e0)
        )
        self.assertTupleEqual(
            s.simplify(s.parse('kg*s/ms^2')),
            ([Unit('kg'), Unit('s^-1')], 1e6)
        )

        # With convering to base units
        self.assertTupleEqual(
            s.simplify(s.parse('mm^2'), base=True),
            ([Unit('m^2')], 1e-6)
        )
        self.assertTupleEqual(
            s.simplify(s.parse('N*s^2'), base=True),
            ([Unit('kg'), Unit('m')], 1e0)
        )
        self.assertTupleEqual(
            s.simplify(s.parse('N*m'), base=True),
            ([Unit('kg'), Unit('m^2'), Unit('s^-2')], 1e0)
        )
        self.assertTupleEqual(
            s.simplify(s.parse('N/mm'), base=True),
            ([Unit('kg'), Unit('s^-2')], 1e3)
        )

    def test_unparse(self):
        s = Scalar(2)

        self.assertEqual(s.unparse(s.parse('')), '')
        self.assertEqual(s.unparse(s.parse('kg^2')), 'kg^2')
        self.assertEqual(s.unparse(s.parse('N*m')), 'N*m')
        self.assertEqual(s.unparse(s.parse('J*K/A*s')), 'J*K/A*s')

    def test_addition(self):
        # Scalars with numbers
        s = Scalar(2, 'cm^2')
        t = Scalar(3, 'cm^2')
        u = Scalar(4, 'm^2')
        v = Scalar(5, 'm')

        # Addition with like units
        self.assertEqual(s + t, Scalar(5, 'cm^2'))
        self.assertEqual(t + s, Scalar(5, 'cm^2'))

        # Addition with unit conversion
        self.assertEqual(s + u, Scalar(40002, 'cm^2'))
        self.assertEqual(u + s, Scalar(4.0002, 'm^2'))

        # Addition with unlike units
        with self.assertRaises(ScalarError):
            s + v

        with self.assertRaises(ScalarError):
            v + s


        # Addition with numbers
        with self.assertRaises(ScalarError):
            s + 2

        with self.assertRaises(ScalarError):
            2 + s

        # Scalars with iterables
        s = Scalar([1, 2], 'cm^2')
        t = Scalar([3, 4], 'cm^2')
        u = Scalar([5, 6] 'm^2')
        v = Scalar([7, 8], 'm')

        # Addition with like units
        self.assertEqual(s + t, Scalar([4, 4], 'cm^2'))
        self.assertEqual(t + s, Scalar([4, 4], 'cm^2'))

        # Addition with unit conversion
        self.assertEqual(s + u, Scalar([50001, 60002], 'cm^2'))
        self.assertEqual(u + s, Scalar([5.0001, 6.0002], 'm^2'))

        # Addition with unlike units
        with self.assertRaises(ScalarError):
            s + v

        with self.assertRaises(ScalarError):
            v + s

        # Addition with numbers
        with self.assertRaises(ScalarError):
            s + np.array([1, 2])

        with self.assertRaises(ScalarError):
            np.array([1, 2]) + s

    def test_subtraction(self):
        # Subtraction with numbers
        s = Scalar(2, 'cm^2')
        t = Scalar(3, 'cm^2')
        u = Scalar(4, 'm^2')
        v = Scalar(5, 'm')

        # Subtraction with like units
        self.assertEqual(s - t, Scalar(-1, 'cm^2'))
        self.assertEqual(t - s, Scalar(1, 'cm^2'))

        # Subtraction with unit conversion
        self.assertEqual(s - u, Scalar(-39998, 'cm^2'))
        self.assertEqual(u - s, Scalar(3.9998, 'm^2'))

        # Subtraction with unlike units
        with self.assertRaises(ScalarError):
            s - v

        with self.assertRaises(ScalarError):
            v - s

        # Subtraction with numbers
        with self.assertRaises(ScalarError):
            s - 2

        with self.assertRaises(ScalarError):
            2 - s

        # Scalars with iterables
        s = Scalar([1, 2], 'cm^2')
        t = Scalar([3, 4], 'cm^2')
        u = Scalar([5, 6] 'm^2')
        v = Scalar([7, 8], 'm')

        # Addition with like units
        self.assertEqual(s - t, Scalar([-2, -2], 'cm^2'))
        self.assertEqual(t - s, Scalar([2, 2], 'cm^2'))

        # Addition with unit conversion
        self.assertEqual(s - u, Scalar([-49999, -59998], 'cm^2'))
        self.assertEqual(u - s, Scalar([4.9999, 5.9998], 'm^2'))

        # Addition with unlike units
        with self.assertRaises(ScalarError):
            s - v

        with self.assertRaises(ScalarError):
            v - s

        # Addition with numbers
        with self.assertRaises(ScalarError):
            s - np.array([1, 2])

        with self.assertRaises(ScalarError):
            np.array([1, 2]) - s

    def test_multiplication(self):
        # Scalars with numbers
        s = Scalar(2, 'cm^2')
        t = Scalar(3, 'cm^2')
        u = Scalar(4, 'm')
        v = Scalar(5, 'kg/s')

        # Multiplication with like units
        self.assertEqual(s * t, Scalar(6, 'cm^4'))
        self.assertEqual(t * s, Scalar(6, 'cm^4'))

        # Multiplication with unit conversion
        self.assertEqual(s * u, Scalar(8, 'cm^2*m'))
        self.assertEqual(u * s, Scalar(8, 'm*cm^2'))

        # Multiplication with unlike units
        self.assertEqual(s * v, Scalar(10, 'cm^2*kg/s'))
        self.assertEqual(v * s, Scalar(10, 'kg*cm^2/s'))

        # Multiplication with numbers
        self.assertEqual(2 * s, Scalar(4, 'cm^2'))
        self.assertEqual(s * 2, Scalar(4, 'cm^2'))

        # Scalars with iterables
        s = Scalar([2, 3], 'cm^2')
        t = Scalar([4, 5], 'cm^2')
        u = Scalar([6, 7], 'm')
        v = Scalar([8, 9], 'kg/s')

        # Multiplication with like units
        self.assertEqual(s * t, Scalar([8, 15], 'cm^4'))
        self.assertEqual(t * s, Scalar([8, 15], 'cm^4'))

        # Multiplication with unit conversion
        self.assertEqual(s * u, Scalar([12, 21], 'cm^2*m'))
        self.assertEqual(u * s, Scalar([12, 21], 'm*cm^2'))

        # Multiplication with unlike units
        self.assertEqual(s * v, Scalar([16, 27], 'cm^2*kg/s'))
        self.assertEqual(v * s, Scalar([16, 27], 'kg*cm^2/s'))

        # Multiplication with numbers
        self.assertEqual(2 * s, Scalar([4, 6], 'cm^2'))
        self.assertEqual(s * 2, Scalar([4, 6], 'cm^2'))
        self.assertEqual(np.array([2, 3]) * s, Scalar([4, 9], 'cm^2'))
        self.assertEqual(s * np.array([2, 3]), Scalar([4, 9], 'cm^2'))

    def test_division(self):
        # Scalars with numbers
        s = Scalar(100, 'cm^2')
        t = Scalar(2, 'cm^2')
        u = Scalar(4, 'm')
        v = Scalar(5, 'kg/s')

        # Division with like units
        self.assertEqual(s / t, Scalar(50, ''))
        self.assertEqual(t / s, Scalar(0.02, ''))

        # Division with unit conversion
        self.assertEqual(s / u, Scalar(25, 'cm^2/m'))
        self.assertEqual(u / s, Scalar(0.04, 'm/cm^2'))

        # Division with unlike units
        self.assertEqual(s / v, Scalar(20, 'cm^2*s/kg'))
        self.assertEqual(v / s, Scalar(0.05, 'kg/s*cm^2'))

        # Division with numbers
        self.assertEqual(2 / s, Scalar(0.02, '/cm^2'))
        self.assertEqual(s / 2, Scalar(50, 'cm^2'))

        # Scalars with iterables
        s = Scalar([100, 100], 'cm^2')
        t = Scalar([2, 4], 'cm^2')
        u = Scalar([5, 10], 'm')
        v = Scalar([20, 25], 'kg/s')

        # Division with like units
        self.assertEqual(s / t, Scalar([50, 25], ''))
        self.assertEqual(t / s, Scalar([0.02, 0.04], ''))

        # Division with unit conversion
        self.assertEqual(s / u, Scalar([20, 10], 'cm^2/m'))
        self.assertEqual(u / s, Scalar([0.05, 0.1], 'm/cm^2'))

        # Division with unlike units
        self.assertEqual(s / v, Scalar([5, 4], 'cm^2*s/kg'))
        self.assertEqual(v / s, Scalar([0.2, 0.25], 'kg/s*cm^2'))

        # Division with numbers
        self.assertEqual(2 / s, Scalar([0.02, 0.02], '/cm^2'))
        self.assertEqual(s / 2, Scalar([50, 50], 'cm^2'))
        self.assertEqual(np.array([2, 4]) / s, Scalar([0.02, 0.04], '/cm^2'))
        self.assertEqual(s / np.array([2, 4]), Scalar([50, 25], 'cm^2'))

    def test_power(self):
        pass

        # Equalies
        # Inequalties

        # String
        pass


class TestUnit(unittest.TestCase):
    def test_init(self):
        # Simplest case is dimensionless unit
        u = Unit('')

        self.assertEqual(u.prefix, '')
        self.assertEqual(u.base, '')
        self.assertEqual(u.power, 1)

        self.assertEqual(u.latex, '')
        self.assertEqual(u.parsed, ['', '', 1])
        self.assertEqual(u.unparsed, '')

        # Unit with no prefix or power
        u = Unit('N')

        self.assertEqual(u.prefix, '')
        self.assertEqual(u.base, 'N')
        self.assertEqual(u.power, 1)

        self.assertEqual(u.latex, 'N')
        self.assertEqual(u.parsed, ['', 'N', 1])
        self.assertEqual(u.unparsed, 'N')

        # Unit with prefix, no power
        u = Unit('mJ')

        self.assertEqual(u.prefix, 'm')
        self.assertEqual(u.base, 'J')
        self.assertEqual(u.power, 1)

        self.assertEqual(u.latex, 'mJ')
        self.assertEqual(u.parsed, ['m', 'J', 1])
        self.assertEqual(u.unparsed, 'mJ')

        # Unit with power, no prefix
        u = Unit('C^2')

        self.assertEqual(u.prefix, '')
        self.assertEqual(u.base, 'C')
        self.assertEqual(u.power, 2)

        self.assertEqual(u.latex, 'C^{2}')
        self.assertEqual(u.parsed, ['', 'C', 2])
        self.assertEqual(u.unparsed, 'C^2')

        # Unit with prefix and power
        u = Unit('kg^2')

        self.assertEqual(u.prefix, 'k')
        self.assertEqual(u.base, 'g')
        self.assertEqual(u.power, 2)

        self.assertEqual(u.latex, 'kg^{2}')
        self.assertEqual(u.parsed, ['k', 'g', 2])
        self.assertEqual(u.unparsed, 'kg^2')

    def test_operations(self):
        u = Unit('kg^2')
        v = Unit('kg^2')
        w = Unit('mJ')

        self.assertEqual(str(u), 'kg^2')

        self.assertTrue(u == v)
        self.assertFalse(u == w)
        self.assertFalse(v == w)

        self.assertFalse(u != v)
        self.assertTrue(u != w)
        self.assertTrue(v != w)


if __name__ == '__main__':
    unittest.main()

