import json
import os
import re

from factors import PREFIXES, UNITS


class UnitError(Exception):
    pass


class Unit:
    """
    TODO: special exceptions for isTemperatureUnit? and isTimeUnit?
    TODO: separate __init__ into parse and add test
    """
    def __init__(self, unit=''):
        # Split prefix and base from power
        splitter = re.split('[\^]', unit)

        if len(splitter) == 1:
            letters = splitter[0]
            self.power = 1
        elif len(splitter) == 2:
            letters, power = splitter
            try:
                self.power = float(power)
            except ValueError:
                raise UnitError(f'"{unit}" should use only numbers after power symbol "^"')

            if self.power.is_integer():
                self.power = int(self.power)
        else:
            raise UnitError(f'"{unit}" should use power symbol "^" only once')

        if not letters.isalpha() and letters != '':
            raise UnitError(f'"{unit}" should use only letters before power symbol "^"')

        # Longest spelled out prefix has five letters, and longest
        # abbreviated prefix has two letters
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
    def base(self):
        return self._base

    @base.setter
    def base(self, base):
        self._base = base

    @property
    def latex(self):
        """Compatible with the "siunitx" package."""
        if self.power == 1:
            latex = f'{self.prefix}{self.base}'
        else:
            latex = f'{self.prefix}{self.base}^{{{self.power}}}'

        return latex

    @property
    def parsed(self):
        return [self.prefix, self.base, self.power]

    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, power):
        self._power = power

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, prefix):
        self._prefix = prefix

    @property
    def unparsed(self):
        if self.power == 1:
            unparsed = f'{self.prefix}{self.base}'
        else:
            unparsed = f'{self.prefix}{self.base}^{self.power}'

        return unparsed

    def __eq__(self, ounit):
        return self.parsed == ounit.parsed

    def __neq__(self, ounit):
        return self.parsed != ounit.parsed

    def __repr__(self):
        return f'Unit({self.unparsed})'

    def __str__(self):
        return self.unparsed

