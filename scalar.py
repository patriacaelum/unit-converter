from .units import Unit


class ScalarError(Exception):
    pass


class Scalar:
    def __init__(self, values, units=''):
        try:
            self._values = np.array(values, dtype=float)
        except:
            raise ScalarError('Values must be a number or an iterable')

        try:
            self._units = self.parse(units)
        except:
            raise ScalarError('Units must be a string')

    def parse(self, units):
        parsed = list()

        sign = 1.0
        for group in units.split('/'):
            for unit in group.split('*'):
                u = Unit(unit)
                u.exponent *= sign
                parsed.append(u)
            sign *= -1.0

        return parsed
