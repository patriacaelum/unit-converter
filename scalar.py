from copy import deepcopy

from .factors import PREFIXES
from .units import Unit


class ScalarError(Exception):
    pass


class Scalar:
    """
    TODO: rename to power
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
        if units is None:
            units = self._units

        factor = 1.0
        based = list()

        for unit in units:
            factor *= self.conversion_factor(unit, Unit(unit.base))
            parsed = self.parse(BASE_UNITS[unit.base])
            for bunit in parsed:
                bunit.power *= unit.power

            based += parsed

        return based, factor

    def conversion_factor(self, ounit, nunit):
        """Calculates the conversion factor when converting from `unit1`
        to `unit2`.
        """
        if ounit.base != nunit.base:
            raise ScalarError(
                f"""Cannot convert {ounit} to {nunit}, base unit must be the
                same."""
            )

        return PREFIXES[ounit.prefix] / PREFIXES[nunit.prefix]

    def convert(self, units):
        if units == self._units:
            return self

        ounits, ofactor = self.simplify(self._units, base=True)
        nunits, nfactor = self.simplify(units, base=True)

        if ounits != nunits:
            raise ScalarError(f'Cannot convert "{self.unparsed}" to "{units}"')

        if self.isTemperature(ounits):
            self._values = self.convert_temperature(ounits, nunits)
        else:
            self._values *= ofactor / nfactor

        self._units = nunits

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

    def isTemperature(self, units):
        """Determines if the units are a measurement of temperature."""
        pass

    def parse(self, units=''):
        parsed = list()

        sign = 1.0
        for group in units.split('/'):
            for unit in group.split('*'):
                u = Unit(unit)
                u.power *= sign
                parsed.append(u)
            sign *= -1.0

        return parsed

    @property
    def parsed(self):
        return self._units

    def simplify(self, units=None, base=False):
        if units is None:
            units = self._units

        if base:
            units = self.base(units)

        factor = 1.0
        stored = list()
        simplified = list()
        for unit in units:
            if unit.base in stored:
                index = stored.index(unit.base)
                factor *= self.conversion_factor(simplified[index], unit)
                simplified[index].power += unit.power
            else:
                simplified.append(unit)
                stored.append(unit.base)

        return simplified, factor

    @property
    def units(self):
        return self._units

    def unparse(self, units=None):
        if units is None:
            units = self._units

        units = deepcopy(units)
        numerator = ''
        denominator = ''

        for unit in u:
            if unit.power >= 0:
                numerator += '*' + str(unit)
            else:
                unit.power *= -1.0
                denominator += '*' + str(unit)

        unparsed = '/'.join(numerator, denominator)

        return unparse

    @property
    def unparsed(self):
        return self.unparsed(self._units)

    @property
    def values(self):
        return self._values

    def __repr__(self):
        return 'Scalar({self._values}, {self._units})'

    def __str__(self):
        return '{self._values} {self.unparse(self._units)}'


def main():
    s = Scalar(2, 'kg')
    print(s.values)


if __name__ == '__main__':
    main()
