import numpy as np
import unittest

from scalar import Scalar
from unit import Unit


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

    def test_operations(self):
        # Addition
        # Subtraction
        # Multiplication
        # Division
        # Power

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

