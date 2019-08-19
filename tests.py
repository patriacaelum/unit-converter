import numpy as np
import unittest

from scalar import Scalar, ScalarError
from unit import Unit, UnitError


class TestScalar(unittest.TestCase):
    def testInit(self):
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

    def testBase(self):
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

    def testConversionFactor(self):
        s = Scalar(2)

        self.assertEqual(s.conversionFactor(Unit('mm'), Unit('m')), 1e-3)
        self.assertEqual(s.conversionFactor(Unit('kg^2'), Unit('mg^2')), 1e12)
        self.assertEqual(s.conversionFactor(Unit('s^-1'), Unit('ms^-1')), 1e-3)

        with self.assertRaises(ScalarError):
            s. conversionFactor(Unit('mm'), Unit('m^2'))

    def testConvert(self):
        # Single unit conversion
        s = Scalar(2, 'm^2')

        self.assertEqual(s.convert('cm^2'), Scalar(20000, 'cm^2'))

        with self.assertRaises(ScalarError):
            s.convert('cm')

        with self.assertRaises(ScalarError):
            s.convert('kg')

        # Iterable unit conversion
        s = Scalar([1, 2], 'm^2')

        self.assertEqual(s.convert('cm^2'), Scalar([10000, 20000], 'cm^2'))

        with self.assertRaises(ScalarError):
            s.convert('cm')

        with self.assertRaises(ScalarError):
            s.convert('kg')

        # Temperature conversion
        s = Scalar(2, 'K')

        self.assertEqual(s.convert('°C'), Scalar(-271.15, '°C'))
        self.assertEqual(s.convert('°F'), Scalar(-456.07, '°F'))

        # Complex unit conversion
        s = Scalar(2, 'N')
        t = Scalar(3, 'J/s')

        self.assertEqual(s.convert('kg*cm/s^2'), Scalar(200, 'kg*cm/s^2'))
        self.assertEqual(t.convert('g*m^3/s^3*m'), Scalar(3000, 'g*m^3/s^3*m'))

    def testConvertTemperature(self):
        # Conversion from kelvin
        s = Scalar(2, 'K')

        self.assertEqual(s.convertTemperature(s.parse('K'), s.parse('°C')), -271.15)
        self.assertEqual(s.convertTemperature(s.parse('K'), s.parse('°F')), -456.07)

        # Conversion from celsius
        s = Scalar(2, '°C')

        self.assertEqual(s.convertTemperature(s.parse('°C'), s.parse('K')), 275.15)
        self.assertEqual(s.convertTemperature(s.parse('°C'), s.parse('°F')), 35.6)

        # Conversion from fahrenheit
        s = Scalar(2, '°F')

        self.assertAlmostEqual(s.convertTemperature(s.parse('°F'), s.parse('K')), 256.4833333)
        self.assertAlmostEqual(s.convertTemperature(s.parse('°F'), s.parse('°C')), -16.6666667)

    def testIsTemperature(self):
        s = Scalar(2, 'K')

        self.assertTrue(s.isTemperature(s.parse('K')))
        self.assertTrue(s.isTemperature(s.parse('°C')))
        self.assertTrue(s.isTemperature(s.parse('°F')))

        self.assertFalse(s.isTemperature(s.parse('kg')))
        self.assertFalse(s.isTemperature(s.parse('K/s')))

    def testParse(self):
        s = Scalar(2)

        self.assertEqual(s.parse(''), [Unit('')])
        self.assertEqual(s.parse('kg^2'), [Unit('kg^2')])
        self.assertEqual(
            s.parse('kg^2*m^3/s^4'),
            [Unit('kg^2'), Unit('m^3'), Unit('s^-4')]
        )

    def testSimplify(self):
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

        # With converting to base units
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

    def testUnparse(self):
        s = Scalar(2)

        self.assertEqual(s.unparse(s.parse('')), '')
        self.assertEqual(s.unparse(s.parse('kg^2')), 'kg^2')
        self.assertEqual(s.unparse(s.parse('N*m')), 'N*m')
        self.assertEqual(s.unparse(s.parse('J*K/A*s')), 'J*K/A*s')

    def testAbsolute(self):
        # Scalar with number
        s = Scalar(2)
        t = Scalar(-3)

        self.assertEqual(abs(s), 2)
        self.assertEqual(abs(t), 3)

        # Scalar with iterable
        s = Scalar([1, -2])

        self.assertEqual(abs(s).tolist(), [1, 2])

    def testAddition(self):
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
        self.assertAlmostEqual(u + s, Scalar(4.0002, 'm^2'))

        # Addition with unlike units
        with self.assertRaises(ScalarError):
            s + v

        with self.assertRaises(ScalarError):
            v + s


        # Addition with numbers
        with self.assertRaises(TypeError):
            s + 2

        with self.assertRaises(TypeError):
            2 + s

        # Scalars with iterables
        s = Scalar([1, 2], 'cm^2')
        t = Scalar([3, 4], 'cm^2')
        u = Scalar([5, 6], 'm^2')
        v = Scalar([7, 8], 'm')

        # Addition with like units
        self.assertEqual(s + t, Scalar([4, 6], 'cm^2'))
        self.assertEqual(t + s, Scalar([4, 6], 'cm^2'))

        # Addition with unit conversion
        self.assertEqual(s + u, Scalar([50001, 60002], 'cm^2'))
        self.assertEqual(u + s, Scalar([50001, 60002], 'cm^2'))

        # Addition with unlike units
        with self.assertRaises(ScalarError):
            s + v

        with self.assertRaises(ScalarError):
            v + s

        # Addition with numbers
        with self.assertRaises(TypeError):
            s + np.array([1, 2])

        with self.assertRaises(TypeError):
            np.array([1, 2]) + s

    def testSubtraction(self):
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
        with self.assertRaises(TypeError):
            s - 2

        with self.assertRaises(TypeError):
            2 - s

        # Scalars with iterables
        s = Scalar([1, 2], 'cm^2')
        t = Scalar([3, 4], 'cm^2')
        u = Scalar([5, 6], 'm^2')
        v = Scalar([7, 8], 'm')

        # Addition with like units
        self.assertEqual(s - t, Scalar([-2, -2], 'cm^2'))
        self.assertEqual(t - s, Scalar([2, 2], 'cm^2'))

        # Addition with unit conversion
        self.assertEqual(s - u, Scalar([-49999, -59998], 'cm^2'))
        self.assertEqual(u - s, Scalar([49999, 59998], 'cm^2'))

        # Addition with unlike units
        with self.assertRaises(ScalarError):
            s - v

        with self.assertRaises(ScalarError):
            v - s

        # Addition with numbers
        with self.assertRaises(TypeError):
            s - np.array([1, 2])

        with self.assertRaises(TypeError):
            np.array([1, 2]) - s

    def testMultiplication(self):
        # Scalars with numbers
        s = Scalar(2, 'cm^2')
        t = Scalar(3, 'cm^2')
        u = Scalar(4, 'm')
        v = Scalar(5, 'kg/s')

        # Multiplication with like units
        self.assertEqual(s * t, Scalar(6, 'cm^4'))
        self.assertEqual(t * s, Scalar(6, 'cm^4'))

        # Multiplication with unit conversion
        self.assertAlmostEqual(s * u, Scalar(8, 'cm^2*m'))
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
        self.assertEqual(s * u, Scalar([1200, 2100], 'cm^3'))
        self.assertEqual(u * s, Scalar([12, 21], 'm*cm^2'))

        # Multiplication with unlike units
        self.assertEqual(s * v, Scalar([16, 27], 'cm^2*kg/s'))
        self.assertEqual(v * s, Scalar([16, 27], 'kg*cm^2/s'))

        # Multiplication with numbers
        self.assertEqual(2 * s, Scalar([4, 6], 'cm^2'))
        self.assertEqual(s * 2, Scalar([4, 6], 'cm^2'))
        self.assertEqual(s * np.array([2, 3]), Scalar([4, 9], 'cm^2'))

    def testDivision(self):
        # Scalars with numbers
        s = Scalar(100, 'cm^2')
        t = Scalar(2, 'cm^2')
        u = Scalar(4, 'm')
        v = Scalar(5, 'kg/s')

        # Division with like units
        self.assertEqual(s / t, Scalar(50, ''))
        self.assertEqual(t / s, Scalar(0.02, ''))

        # Division with unit conversion
        self.assertEqual(s / u, Scalar(0.25, 'cm'))
        self.assertEqual(u / s, Scalar(400, '/m'))

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
        self.assertEqual(u / s, Scalar([500, 1000], '/m'))

        # Division with unlike units
        self.assertEqual(s / v, Scalar([5, 4], 'cm^2*s/kg'))
        self.assertEqual(v / s, Scalar([0.2, 0.25], 'kg/s*cm^2'))

        # Division with numbers
        self.assertEqual(2 / s, Scalar([0.02, 0.02], '/cm^2'))
        self.assertEqual(s / 2, Scalar([50, 50], 'cm^2'))
        self.assertEqual(s / np.array([2, 4]), Scalar([50, 25], 'cm^2'))

    def testPower(self):
        # Scalar with number
        s = Scalar(2, 'kg')

        self.assertEqual(s**3, Scalar(8, 'kg^3'))

        # Scalar with iterables
        s = Scalar([2, 3], 'cm/s')

        self.assertEqual(s**3, Scalar([8, 27], 'cm^3/s^3'))

    def testEquality(self):
        # Scalars with numbers
        s = Scalar(2, 'kg')
        t = Scalar(2, 'kg')
        u = Scalar(2000, 'g')
        v = Scalar(2, 'kg*kg/kg')
        w = Scalar(2, 'kg^2')

        self.assertTrue(s == t)
        self.assertTrue(s == u)
        self.assertTrue(s == v)
        self.assertFalse(s == w)

        # Scalars with iterables
        s = Scalar([1, 2], 'kg')
        t = Scalar([1, 2], 'kg')
        u = Scalar([1000, 2000], 'g')
        v = Scalar([1, 2], 'kg*kg/kg')
        w = Scalar([1, 2], 'kg^2')

        self.assertTrue(s == t)
        self.assertTrue(s == u)
        self.assertTrue(s == v)
        self.assertFalse(s == w)

    def testInequality(self):
        # Scalars with numbers
        s = Scalar(2, 'kg')
        t = Scalar(2, 'kg')
        u = Scalar(2000, 'g')
        v = Scalar(2, 'kg*kg/kg')
        w = Scalar(2, 'kg^2')

        self.assertFalse(s != t)
        self.assertFalse(s != u)
        self.assertFalse(s != v)
        self.assertTrue(s != w)

        # Scalars with iterables
        s = Scalar([1, 2], 'kg')
        t = Scalar([1, 2], 'kg')
        u = Scalar([1000, 2000], 'g')
        v = Scalar([1, 2], 'kg*kg/kg')
        w = Scalar([1, 2], 'kg^2')

        self.assertFalse(s != t)
        self.assertFalse(s != u)
        self.assertFalse(s != v)
        self.assertTrue(s != w)

    def testString(self):
        s = Scalar(2, 'kg^2')

        self.assertEqual(str(s), '2.0 kg^2')


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

