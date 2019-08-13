import json
import os
import re


path = os.path.dirname(os.path.abspath(__file__))

# TODO: just import the list?
with open(os.path.join(path, 'prefixes.json'), 'r') as file:
    PREFIXES = json.load(file)

with open(os.path.join(path, 'units.json'), 'r') as file:
    UNITS = json.load(file)


class UnitError(Exception):
    pass


class Unit:
    """
    TODO: special exceptions for isTemperatureUnit? and isTimeUnit?
    """
    def __init__(self, unit=''):
        # TODO: add try-except if split is more or less than two elements
        splitter = re.split('[\^]', unit)

        if len(splitter) != 2:
            raise UnitError('"{unit}" should use power symbol "^" only once')

        if splitter[0].isalpha():
            letters = splitter[0]
        else:
            raise UnitError('"{unit}" should use only letters before power symbol "^"')

        try:
            self.power = float(splitter[1])
        except ValueError:
            raise UnitError('"{unit}" should use only numbers after power symbol "^"')

        if self.power.is_integer():
            self.power = int(self.power)

        # Longest spelled out prefix has five letters, and longest abbreviated prefix has two
        # letters
        if len(letters) < 5:
            length = 2
        else:
            length = 5

        for i in range(length):
            if letters[:i] in PREFIXES.keys() and letters[i:] in UNITS:
                self.prefix = letters[:i]
                self.base = letters[i:]
                break
        else:
            raise UnitError(f'"{unit}" cannot be parsed')

    @property
    def latex(self):
        return f'{self.prefix}{self.base}^{{{self.power}}}'

    @property
    def parsed(self):
        return [self.prefix, self.base, self.power]

    @property
    def unparsed(self):
        return f'{self.prefix}{self.base}^{self.power}'

    def __eq__(self):
        # TODO: equate even if order is different
        pass

    def __repr__(self):
        return f'Scalar({self.unparsed})'

    def __str__(self):
        return self.unparsed


def main():
    unit = Unit('kg^2')
    print(unit.parsed)
    print(unit.unparsed)
    print(unit.latex)
    print(unit)


if __name__ == '__main__':
    main()
