mks_units
=========

Simple MKS units library in Python (designed for 3.0+).

This library is an attempt to produce a simple yet robust unit library, using
a technique inspired by OpenFOAM's type checking.  The library keeps a 7-vector
component for the power of each of the SI base units.

Consider the following example:
    >>> from mks_units import *
    >>> x = Unit(5, "mm")
    >>> y = Unit(5, "m s^-1")
    >>> "%s" % (x*y)
    '0.025000 m^2 s^-1'

Units can be passed as a space-separated list of valid units to numeric powers.

Internally, `mks_units` converts all types to powers of the SI base units, but 
can convert back fairly easily:
    >>> "{0:1.5f in^2 min^-1}.format(x*y)
    '2325.00465 in^2 min^-1'
    >>> (x*y).value_as("in^2 min^-1")
    2325.0046500093003

`mks_units` supports all meaninful math functions.

Additional units can be added to `mks_units.UNITS` to facilitate additional 
applications.

