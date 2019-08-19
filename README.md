# Unit Converter

Just a simple unit converter written in Python.

## Usage

```python
from unit_converter import Scalar

# Create Scalar objects
s = Scalar(2000, 'g')
t = Scalar(3, 'm')

# Units can be converted
s.convert('kg')

# Units with the same unit can be added or subtracted
print(s + s)    # 6.0 m

# Units can be multiplied or divided
print(s * t)    # 6.0 kg*m

# More complex unit conversions are also possible
u = s * t / Scalar(1, 's^-2')
print(u)    # 6.0 kg*m/s^2

u.convert('J/m')
print(u)    # 6.0 J/m

# Scalar objects can also store numpy arrays
v = Scalar([1, 2, 3], 'cm')
print(v**3)    # [1, 8, 27] cm^3
```
