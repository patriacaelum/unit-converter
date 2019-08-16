import numpy as np

from collections import Counter
from copy import deepcopy

from factors import BASES, PREFIXES
from unit import Unit


class ScalarError(Exception):
    pass


class Scalar:
    """
    """
    def __init__(self, values, units=''):
        try:
            self._values = np.array(values, dtype=float)
        except:
            raise ScalarError('Values must be a number or an iterable')

        try:
            self._units = self.parse(units)
        except:
            raise ScalarError('Units must be a string')

    def base(self, units=None):
        """Reduces `units` to base SI units as specified in `factors.py`

        The base SI units are limited to:

        - kg (kilogram)
        - m (metre)
        - s (second)
        - A (ampere)
        - K (kelvin)
        - cd (candela)
        - mol (mole)

        All other derived units are then converted to these base units.
        The base unit representations are specified in `BASES` from
        `factors.py`. For example:

        - mm    -> (m, 1e-3)
        - g     -> (kg, 1e-3)
        - kN^2  -> (kg^2*m^2/s^4, 1e6)
        - N*s   -> (kg*m/s, 1e0)

        Parameters
        ------------
        units: (list) a list of `Unit` objects.

        Returns
        ------------
        (tuple) a tuple with two elements. The first is a list of `Unit`
        objects, and the second is the multiplicative factor when
        converting to base units.
        """
        if units is None:
            units = self._units

        factor = 1.0
        based = list()

        for unit in units:
            # 'g' is special since it's usually in 'kg'
            if unit.base == 'g':
                factor *= self.conversion_factor(unit, Unit(f'kg^{unit.power}'))
            else:
                factor *= self.conversion_factor(unit, Unit(f'{unit.base}^{unit.power}'))

            parsed = self.parse(BASES[unit.base])
            for index in range(len(parsed)):
                parsed[index].power *= unit.power

            based += parsed

        return based, factor

    def conversion_factor(self, ounit, nunit):
        """Calculates the conversion factor from the old unit `ounit` to
        the new unit `nunit`.

        This conversion assumes the bases and powers are the same, and
        only the prefixes differ. For example:

        - mm -> m = 1e-3
        - kg -> mg = 1e6

        Parameters
        ------------
        ounit: (Unit) the current unit being converted from.
        nunit: (Unit) the final unit being converted to.

        Returns
        ------------
        (float) the multiplicative factor when converting from `ounit` to
        `nunit`.
        """
        if ounit.base != nunit.base or ounit.power != nunit.power:
            raise ScalarError(
                f"""Cannot convert {ounit} to {nunit}, base unit must be the
                same."""
            )

        factor = (
            PREFIXES[ounit.prefix]**ounit.power
            / PREFIXES[nunit.prefix]**nunit.power
        )

        return factor

    def convert(self, units):
        units = self.parse(units)

        if Counter(map(str, units)) == Counter(map(str, self._units)):
            return self

        ounits, ofactor = self.simplify(self._units, base=True)
        nunits, nfactor = self.simplify(units, base=True)

        if Counter(map(str, ounits)) != Counter(map(str, nunits)):
            raise ScalarError(f'Cannot convert "{self.unparsed}" to "{units}"')

        if self.isTemperature(ounits):
            self._values = self.convert_temperature(ounits, nunits)
        else:
            self._values *= ofactor / nfactor

        self._units = units

        return self

    def convert_temperature(ounit, nunit):
        """Converts between temperature units.

        This is a special case due to temperature having the same scale
        but with different zeros, and is only used when converting
        between temperature units.
        """
        if nunit == 'K':
            if ounit == '°C':
                values = self._values + 273.15
            elif ounit == '°F':
                values = (5.0 / 9.0) * (self._values + 459.67)
        elif nunit == '°C':
            if ounit == 'K':
                values = self._values - 273.15
            elif ounit == '°F':
                values = (5.0 / 9.0) * (self._values - 32.0)
        elif nunit == '°F':
            if nunit == 'K':
                values = (9.0 / 5.0) * self._values - 459.67
            elif nunit == '°C':
                values = (9.0 / 5.0) * self._values + 32.0
        else:
            raise ScalarError(
                """Could not perform temperature conversion from "{ounit}" to
                "{nunit}"""""
            )

        return values

    def is_temperature(self, units):
        """Determines if the units are a measurement of temperature."""
        pass

    @property
    def latex(self):
        """A LaTeX representation of the units, compatible with the
        "siunitx" package.

        Returns
        ---------
        (str) a LaTeX representation of the units.
        """
        units = deepcopy(self._units)
        numerator = list()
        denominator = list()

        for unit in units:
            if unit.power >= 0:
                numerator.append(unit.latex)
            else:
                denominator.append(unit.latex)

        if len(denominator) == 0:
            latex = '.'.join(numerator)
        elif len(numerator) == 0:
            latex = '.'.join(denominator)
        else:
            latex = '.'.join(['.'.join(numerator), '.'.join(denominator)])

        return latex

    def parse(self, units=''):
        """Parses `units` into a list of `Unit` objects.

        This method can parse multiple units separated by the
        multiplication symbol "*" or division symbol "/". For example:

        - A/s -> [Unit(A), Unit(s^-1)]
        - kg*m^2/s^2 -> [Unit(kg), Unit(m^2), Unit(s^-2)]

        Parameters
        ------------
        units: (str) a string of units.

        Returns
        ------------
        (list) a list of `Unit` objects.
        """
        parsed = list()

        sign = 1
        groups = units.split('/')

        # Remove empty numerator (if numerator is empty)
        if len(groups) > 1 and groups[0] == '':
            del groups[0]

        for group in groups:
            for unit in group.split('*'):
                u = Unit(unit)
                u.power *= sign
                parsed.append(u)
            sign *= -1

        return parsed

    @property
    def parsed(self):
        """The parsed units as a list of `Unit` objects.

        Returns
        ---------
        (list) a list of `Unit` objects.
        """
        return self._units

    def simplify(self, units=None, base=False):
        """Simplifies the list of `Unit` objects.

        This method simplifies `units` by grouping together `Unit`
        objects with the same base and summing their powers. By using the
        `base` flag, derived units are converted into base units before
        being simplified. For example:

        - m^2/m -> m
        - N*s -> kg*m^2/s^2

        Parameters
        ------------
        units: (list) a list of `Unit` objects.
        base:  (bool) indicates if the `units` are to be converted to
               base units. See the `base()` method for more information.

        Returns
        ------------
        (tuple) a tuple with two elements. The first is the simplified
        list of `Unit` objects. The second is a float representing the
        multiplicative factor when converting from the previous units to
        the simplified units. The factor is typically relevant only when
        mixing prefixes or when simplifying to base units.
        """
        if units is None:
            units = self._units

        if isinstance(units, str):
            units = self.parse(units)

        factor = 1.0

        if base:
            units, base_factor = self.base(units)
            factor *= base_factor

        stored = list()
        simplified = list()
        for unit in units:
            if unit.base in stored:
                index = stored.index(unit.base)
                factor *= self.conversion_factor(
                    unit,
                    Unit(f'{simplified[index].prefix}{stored[index]}^{unit.power}')
                )
                simplified[index].power += unit.power

                if simplified[index].power == 0:
                    del stored[index]
                    del simplified[index]
            else:
                simplified.append(unit)
                stored.append(unit.base)

        return simplified, factor

    @property
    def units(self):
        """The unparsed units.

        Returns
        ---------
        (str) the string representation of the units.
        """
        return self.unparse(self._units)

    def unparse(self, units=None):
        """Unparses the list of `Unit` objects into a string.

        Parameters
        ------------
        units: (list) a list of `Unit` objects.

        Returns
        ------------
        (str) the string representation of `units`.
        """
        if units is None:
            units = self._units

        units = deepcopy(units)
        numerator = list()
        denominator = list()

        for unit in units:
            if unit.power >= 0:
                numerator.append(str(unit))
            else:
                unit.power *= -1
                denominator.append(str(unit))

        if len(denominator) == 0:
            unparsed = '*'.join(numerator)
        elif len(numerator) == 0:
            unparsed = '/' + '*'.join(denominator)
        else:
            unparsed = '/'.join(['*'.join(numerator), '*'.join(denominator)])

        return unparsed

    @property
    def unparsed(self):
        """The unparsed units, equivalent to the `units` property.

        Returns
        ---------
        (str) the string representation of the units.
        """
        return self.unparse(self._units)

    @property
    def values(self):
        """The given values in the current unit.

        Returns
        ---------
        (numpy.array) the array of values.
        """
        return self._values

    def __add__(self, oscalar):
        scalar = deepcopy(self)

        try:
            scalar._values += oscalar.convert(scalar.units).values
        except ScalarError:
            raise ScalarError(
                'Cannot add scalars with units {scalar.units} and {oscalar.units}'
            )
        else:
            raise ScalarError(
                '"Scalar" objects can only be added with other "Scalar" objects'
            )

        return scalar

    def __eq__(self, oscalar):
        return np.abs(self.values - oscalar.convert(self.units).values) == 0

    def __ge__(self, oscalar):
        return self.values >= oscalar.convert(self.units).values

    def __gt__(self, oscalar):
        return self.values > oscalar.convert(self.units).values

    def __le__(self, oscalar):
        return self.values <= oscalar.convert(self.units).values

    def __len__(self):
        return len(self.values)

    def __lt__(self, oscalar):
        return self.values < oscalar.convert(self.units).values

    def __mul__(self, oscalar):
        scalar = deepcopy(self)

        try:
            scalar.values *= float(oscalar)
        except TypeError:
            scalar._units += oscalar._units
            scalar._units, factor = scalar.simplify(scalar._units)
            scalar._values *= oscalar._values * factor
        else:
            raise ScalarError(
                """Scalar" objects can only be multiplied with other "Scalar" objects or numbers"""
            )

        return scalar

    def __neq__(self, oscalar):
        return np.abs(self.values - oscalar.convert(self.units).values) != 0

    def __pow__(self, power):
        scalar = deepcopy(self)

        scalar._values **= power
        for index in range(len(scalar._units)):
            scalar._units[index].power *= power

        return Scalar

    def __reduce__(self):
        return (self.__class__, (self.values, self.units))

    def __repr__(self):
        return f'Scalar({self._values}, {self._units})'

    def __rmul__(self, oscalar):
        scalar = deepcopy(self)

        try:
            scalar._values *= oscalar
        except TypeError:
            raise ScalarError(
                """"Scalar" objects can only be multiplied with other "Scalar" objects or
                numbers"""
            )

        return scalar

    def __rtruediv__(self, oscalar):
        scalar = deepcopy(self)

        try:
            scalar._values = oscalar / scalar.values
        except TypeError:
            raise ScalarError(
                '"Scalar" objects can only be divided with other "Scalar" objects or numbers'
            )

        for index in range(len(scalar._units)):
            scalar._units[index].power *= -1

        return scalar

    def __str__(self):
        return f'{self._values} {self.unparse(self._units)}'

    def __sub__(self, oscalar):
        scalar = deepcopy(self)

        try:
            scalar._values -= oscalar.convert(scalar.units).values
        except ScalarError:
            raise ScalarError(
                'Cannot subtract scalars with units {scalar.units} and {oscalar.units}'
            )
        else:
            raise ScalarError(
                '"Scalar" objects can only be subtracted with other "Scalar" objects'
            )

        return scalar

    def __truediv__(self, oscalar):
        scalar = deepcopy(self)

        try:
            scalar._values /= float(oscalar)
        except TypeError:
            for index in range(len(oscalar._units)):
                oscalar._units[index].power *= -1

            scalar._units += oscalar._units
            scalar._units, factor = scalar.simplify(scalar._units)
            scalar._values *= factor / oscalar._values
        else:
            raise ScalarError(
                '"Scalar" objects can only be divided with other "Scalar" objects or numbers'
            )

        return scalar


def main():
    a = Scalar(3, 'kg')
    b = Scalar(2000, 'g')


if __name__ == '__main__':
    main()
