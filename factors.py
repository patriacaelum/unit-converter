# TODO: litre, minutes, hours, days, farenheight, imperial units

PREFIXES = {
    'yotta': 1e24,
    'Y': 1e24,
    'zetta': 1e21,
    'Z': 1e21,
    'exa': 1e18,
    'E': 1e18,
    'peta': 1e15,
    'P': 1e15,
    'tera': 1e12,
    'T': 1e12,
    'giga': 1e9,
    'G': 1e9,
    'mega': 1e6,
    'M': 1e6,
    'kilo': 1e3,
    'k': 1e3,
    'hecto': 1e2,
    'h': 1e2,
    'deca': 1e1,
    'da': 1e1,
    '': 1e0,
    'deci': 1e-1,
    'd': 1e-1,
    'centi': 1e-2,
    'c': 1e-2,
    'milli': 1e-3,
    'm': 1e-3,
    'micro': 1e-6,
    'u': 1e-6,
    'μ': 1e-6,
    'nano': 1e-9,
    'n': 1e-9,
    'pico': 1e-12,
    'p': 1e-12,
    'femto': 1e-15,
    'f': 1e-15,
    'atto': 1e-18,
    'a': 1e-18,
    'zepto': 1e-21,
    'z': 1e-21,
    'yocto': 1e-24,
    'y': 1e-24,
}

UNITS = [
    '',
    'metre',
    'meter',
    'm',
    'gram',
    'g',
    'second',
    's',
    'ampere',
    'A',
    'kelvin',
    'K',
    'candela',
    'cd',
    'mole',
    'mol',
    'volt',
    'V',
    'ohm',
    'Ω',
    'tesla',
    'T',
    'weber',
    'Wb',
    'farad',
    'F',
    'henry',
    'H',
    'siemens',
    'S',
    'Coulomb',
    'C',
    'watt',
    'W',
    'newton',
    'N',
    'joule',
    'J',
    'pascal',
    'Pa',
    'Becquerel',
    'Bq',
    'sievert',
    'Sv',
    'celsius',
    '°C',
    'fahrenheit',
    '°F',
    'katal',
    'kat',
    'hertz',
    'Hz',
]

BASES = {
    'm': 'm',
    'g': 'kg',
    's': 's',
    'A': 'A',
    'K': 'K',
    'cd': 'cd',
    'mol': 'mol',
    'V': 'kg*m^2/A*s^3',
    'Ω': 'kg*m^2/A^2*s^3',
    'T': 'kg/A*s^2',
    'Wb': 'kg*m^2/A*s^2',
    'F': 'A^2*s^4/kg*m^2',
    'H': 'kg*m^2/A^2*s^2',
    'S': 'A^2*s^3/kg*m^2',
    'C': 'A*s',
    'W': 'kg*m^2/s^3',
    'N': 'kg*m/s^2',
    'J': 'kg*m^2/s^2',
    'Pa': 'kg*m/s^2',
    'Bq': '/s',
    'Sv': 'm^2/s^2',
    '°C': 'K',
    'kat': 'mol/s',
    'Hz': '/s',
}

