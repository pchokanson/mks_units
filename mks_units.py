#! /usr/bin/env python
# mks_units.py
#
# Copyright (c) 2014 Peter Hokanson
# Distributed under the terms of the MIT license (see LICENSE)
#

"""SI MKS units implementation in Python, meant to simplify engineering 
calculations where units are important.  The technique used for this follows
that used by OpenFOAM: a seven-element vector is kept with the power of each
of the SI base units."""

from __future__ import division

from fractions import Fraction
import numbers

# The following are the official SI base units, in our order:
BASE_UNITS = ("kg", "m", "s", "K", "mol", "A", "cd")

# The following table is sourced from Wikipedia: SI derived unit
SI_UNITS = {
	# Base units
	#         kg   m,  s,  K, mol,  A, cd
	""    : (  0,  0,  0,  0,   0,  0,  0), # unitless
	"kg"  : (  1,  0,  0,  0,   0,  0,  0), # kilogram (mass)
	"m"   : (  0,  1,  0,  0,   0,  0,  0), # meter (length)
	"s"   : (  0,  0,  1,  0,   0,  0,  0), # second (time)
	"K"   : (  0,  0,  0,  1,   0,  0,  0), # kelvin (temperature)
	"mol" : (  0,  0,  0,  0,   1,  0,  0), # moles (amount of substance)
	"A"   : (  0,  0,  0,  0,   0,  1,  0), # ampere (electric current)
	"cd"  : (  0,  0,  0,  0,   0,  0,  1), # candela (luminous intensity)
	# Derived units
	#         kg   m,  s,  K, mol,  A, cd
	"Hz"  : (  0,  0, -1,  0,   0,  0,  0), # hertz (frequency)
	"rad" : (  0,  0,  0,  0,   0,  0,  0), # radian (angle)
	"sr"  : (  0,  0,  0,  0,   0,  0,  0), # steradian (solid angle)
	"N"   : (  1,  1, -2,  0,   0,  0,  0), # newton (force, weight)
	"Pa"  : (  1, -1, -2,  0,   0,  0,  0), # pascal (pressure, stress)
	"J"   : (  1,  2, -2,  0,   0,  0,  0), # joule (energy, work, heat)
	"W"   : (  1,  2, -3,  0,   0,  0,  0), # watt (power, radiant flux)
	"C"   : (  0,  0,  1,  0,   0,  1,  0), # coulomb (charge)
	"V"   : (  1,  2, -3,  0,   0, -1,  0), # volt (potential difference)
	"F"   : ( -1, -2,  4,  0,   0,  2,  0), # farad (capacitance)
	"ohm" : (  1,  2, -3,  0,   0, -2,  0), # ohm (resistance, impedance)
	"S"   : ( -1, -2,  3,  0,   0,  2,  0), # siemens (conductance)
	"Wb"  : (  1,  2, -2,  0,   0, -1,  0), # weber (magnetic flux)
	"T"   : (  1, -2,  0,  0,   0, -1,  0), # tesla (magnetic field strength)
	"H"   : (  1,  2, -2,  0,   0, -2,  0), # henry (inductance)
	"lm"  : (  0,  0,  0,  0,   0,  0,  1), # lumen (luminous flux) [cd-sr]
	"lx"  : (  0, -2,  0,  0,   0,  0,  1), # lux (illuminance)
	"Bq"  : (  0,  0, -1,  0,   0,  0,  0), # becquerel (radioactivity)
	"Gy"  : (  0,  2, -2,  0,   0,  0,  0), # gray (absorbed dose)
	"Sv"  : (  0,  2, -2,  0,   0,  0,  0), # sievert (equivalent dose)
	"kat" : (  0,  0, -1,  0,   1,  0,  0)  # katal (catalytic activity)
}

UNITS = {}

UNITLESS = (0, 0, 0, 0, 0, 0, 0)

class Unit(object):
	"""Unit type that stores a vector of SI base unit orders.  All SI-derived
	units are constructed as the product of powers of base units."""
	
	__slots__ = ["value", "units"]
	
	
	def __init__(self, value, units):
		"""Construct a Unit object with a given numeric value and unit type.  The
		type may either be given as a 7-element array or as a space-separated string
		of base and derived units with numeric powers.
		
		For the string formatting, SI units are separated by spaces and given
		exponents with the ^ operator.  """
		self.value = value
		
		if units is None:
			self.units = UNITLESS
		elif isinstance(units, (list, tuple)):
			# User has given us a direct list or tuple of our unit powers
			assert len(units) == 7, \
			       "Unexpected number of base unit terms in list %s" % units
			self.units = tuple([Fraction(i) for i in units])
		elif isinstance(units, str):
			scale_units = self.string_to_scale_unit(units)
			#print("scale_units: %s" % scale_units)
			self.value *= scale_units.value
			self.units = scale_units.units
		assert isinstance(self.units, tuple) and len(self.units) == 7, \
		       "Invalid units: %r" % self.units
	
	def __repr__(self):
		return "Unit(%f, %s)" % (self.value, self.units)
	
	def __str__(self):
		return self.to_string()
	
	def __format__(self, formatstring):
		split_string = formatstring.split(maxsplit=1)
		if len(split_string) == 0:
			return self.to_string()
		if len(split_string) == 1:
			numformat = split_string[0]
			
			# There is probably a better way to format self.value, but this works
			# for now.
			return ("%"+numformat) % self.value + self.units_to_string(self.units)
		else:
			# Divide the unit by the scaled unit, which should produce a unitless
			# value that is in the desired units
			numformat, units = split_string
			scale_unit = self.string_to_scale_unit(units)
			assert((self / scale_unit).units == UNITLESS)
			scale_value = (self / scale_unit).value
			
			return ("%"+numformat) % scale_value + (" %s" % units)
	
	def value_as(self, units):
		"""Return numeric value in given units."""
		if isinstance(units, str):
			scale_unit = self.string_to_scale_unit(units)
			assert((self / scale_unit).units == UNITLESS)
			return (self / scale_unit).value
			
		elif isinstance(units, tuple):
			# This doesn't make much sense to call, since it's already in mks
			scale_unit = Unit(1, units)
			assert((self / scale_unit).units == UNITLESS)
			return self.value
	
	@staticmethod
	def units_to_string(units):
		unit_string = ""
		for unit, power in zip(BASE_UNITS, units):
			if power == 0: # This unit isn't present
				pass 
			elif power == 1: # Implicit exponent
				unit_string += " %s" % unit
			elif isinstance(power, Fraction): # Fraction case
				unit_string += " %s^%s" % (unit, power)
			else: # Generic numeric
				unit_string += " %s^%f" % (unit, power)
		return unit_string
	
	def to_string(self, formatstring="%f"):
		"""More option-ful string conversion function"""
		unit_string = self.units_to_string(self.units)
		return (formatstring +"%s") % (self.value, unit_string)
	
	def to_LaTeX(self):
		return ""
	
	@staticmethod
	def string_to_scale_unit(unit_string):
		# Accumulator begins dimensionless
		scale_unit = Unit(1, UNITLESS)
		
		# For each whitespace-delimited string:
		for s in unit_string.split():
			# Split each unit into a base and a power
			base, sep, power = s.partition('^')
			
			# Check for implicit '1' exponents, otherwise parse the string as a 
			# fraction
			if power == "":
				power = Fraction(1,1)
			else:
				power = Fraction(power)
			
			# Exponentiate this base unit and accumulate
			# Note that this scales the multiplier with the unit, which should be
			# the expected behavior: 4 (cm^2) != (4 cm)^2
			scale_unit *= UNITS[base] ** power
		
		assert isinstance(scale_unit.units, tuple) and len(scale_unit.units) == 7, \
		       "Invalid units: %r" % scale_unit.units
		
		return scale_unit
	
	@staticmethod
	def check_unit_vector(u):
		if not isinstance(u, tuple):
			return False
		elif len(u) != 7:
			return False
		return True
	
	@staticmethod
	def mult_unit_vectors(u1, u2):
		assert Unit.check_unit_vector(u1), "Unit vector invalid: %s" % u1
		assert Unit.check_unit_vector(u2), "Unit vector invalid: %s" % u2
		return tuple([sum(x) for x in zip(u1, u2)])
	
	@staticmethod
	def pow_unit_vector(u1, n):
		assert Unit.check_unit_vector(u1), "Unit vector invalid: %s" % u1
		return tuple([n * x for x in u1])
	
	@staticmethod
	def match_unit_vectors(u1, u2):
		assert Unit.check_unit_vector(u1), "Unit vector invalid: %s" % u1
		assert Unit.check_unit_vector(u2), "Unit vector invalid: %s" % u2
		return all([x1 == x2 for x1, x2 in zip(u1, u2)])
	
	@staticmethod
	def unitless_vector(u):
		assert Unit.check_unit_vector(u), "Unit vector invalid: %s" % u
		return all([x1 == 0 for x1 in u])
	
	# Silently upconvert numerics to unitless for calculations
	@staticmethod
	def coerce_to_unit(n):
		if isinstance(n, numbers.Number):
			return Unit(n, UNITLESS)
		else:
			return n
	
	def match_units(self, other):
		"""Return true if self and other are of matching units.  Used for addition
		and subtraction, as well as the comparison operations."""
		return Unit.match_unit_vectors(self.units, other.units)
	
	def __lt__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		if self.match_units(other_unit):
			return self.value < other_unit.value
		else: return NotImplemented
	
	def __le__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		if self.match_units(other_unit):
			return self.value <= other_unit.value
		else: return NotImplemented
	
	def __eq__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		if self.match_units(other_unit):
			return self.value == other_unit.value
		else: return NotImplemented
	
	def __ne__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		if self.match_units(other_unit):
			return self.value != other_unit.value
		else: return NotImplemented
	
	def __gt__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		if self.match_units(other_unit):
			return self.value > other_unit.value
		else: return NotImplemented
	
	def __ge__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		if self.match_units(other_unit):
			return self.value >= other_unit.value
		else: return NotImplemented
	
	def __add__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		if self.match_units(other_unit):
			return Unit(self.value + other_unit.value, self.units)
		else: return NotImplemented
	
	def __radd__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		if self.match_units(other_unit):
			return Unit(other_unit.value + self.value, self.units)
		else: return NotImplemented
	
	def __sub__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		if self.match_units(other_unit):
			return Unit(self.value - other_unit.value, self.units)
		else: return NotImplemented
	
	def __rsub__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		if self.match_units(other_unit):
			return Unit(other_unit.value - self.value, self.units)
		else: return NotImplemented
	
	def __mul__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		new_unit_vector = Unit.mult_unit_vectors(self.units, other_unit.units)
		return Unit(self.value * other_unit.value, new_unit_vector)
	
	def __rmul__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		new_unit_vector = Unit.mult_unit_vectors(self.units, other_unit.units)
		return Unit(other_unit.value * self.value, new_unit_vector)
	
	def __truediv__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		other_unit_inv = Unit(other_unit.value, tuple([-x for x in other_unit.units]))
		new_unit_vector = Unit.mult_unit_vectors(self.units, other_unit_inv.units)
		return Unit(self.value / other_unit.value, new_unit_vector)
	
	def __rtruediv__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		self_unit_inv = Unit(self.value, tuple([-x for x in self.units]))
		new_unit_vector = Unit.mult_unit_vectors(self_unit_inv.units, other_unit.units)
		return Unit(other_unit.value / self.value, new_unit_vector)

	def __pow__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		# It's only valid to do powers of unitless values
		if other_unit.match_units(Unit(1,UNITLESS)):
			new_unit_vector = tuple([x*other_unit.value for x in self.units])
			return Unit(pow(self.value, other_unit.value), new_unit_vector)
		else:
			return NotImplemented
	
	def __rpow__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		if self.match_units(Unit(1,UNITLESS)):
			new_unit_vector = tuple([x*self.value for x in other_unit.units])
			return Unit(pow(other_unit.value, self.value), new_unit_vector)
		else:
			return NotImplemented
	
	def __float__(self):
		return float(self.value)
	
	def __int__(self):
		return int(self.value)
	
	def __complex__(self):
		return complex(self.value)
	
	def __neg__(self):
		return Unit(-self.value, self.units)
	
	def __pos__(self):
		return Unit(-self.value, self.units)
	
	def __abs__(self):
		return Unit(abs(self.value), self.units)
	
	def __nonzero__(self):
		return bool(self.value)

SI_PREFIXES = {
	"Y" : 1e24,  # yotta
	"Z" : 1e21,  # zetta
	"E" : 1e18,  # exa
	"P" : 1e15,  # peta
	"T" : 1e12,  # tera
	"G" : 1e9,   # giga
	"M" : 1e6,   # mega
	"k" : 1e3,   # kilo
	"h" : 1e2,   # hecto
	"da": 1e1,   # deca
	""  : 1e0,   # none
	"d" : 1e-1,  # deci
	"c" : 1e-2,  # centi
	"m" : 1e-3,  # milli
	"u" : 1e-6,  # micro (ASCII limitation)
	"n" : 1e-9,  # nano
	"p" : 1e-12, # pico
	"f" : 1e-15, # femto
	"a" : 1e-18, # atto
	"z" : 1e-21, # zepto
	"y" : 1e-24  # yocto
}

for u in SI_UNITS.keys():
	UNITS[u] = Unit(1, SI_UNITS[u])
	if u == "":
		UNITS[u] = SI_UNITS[u]
	elif u == "kg": 
		# Because they had to go make the base unit for mass the gram, I have to
		# do this.  I'd advocate for mgs, personally.
		for p in SI_PREFIXES.keys():
			if p != "k":
				UNITS[p + "g"] = Unit(1e-3*SI_PREFIXES[p], SI_UNITS[u])

	else:
		for p in SI_PREFIXES.keys():
			if p != "":
				UNITS[p + u] = Unit(SI_PREFIXES[p], SI_UNITS[u])


NON_SI_UNITS = {
	"L"   : Unit(1e-3, "m^3"),            # liter
	"mL"  : Unit(1e-6, "m^3"),            # milliliter
	"min" : Unit(60, "s"),                # minute
	"h"   : Unit(60 * 60, "s"),           # second
	"d"   : Unit(24 * 60 * 60, "s"),      # day
	"ha"  : Unit(1e4, "m^2"),             # hectare
	"t"   : Unit(1e3, "kg"),              # tonne (metric)
	"eV"  : Unit(1.6021765314e-19, "J"),  # electronvolt
	"Da"  : Unit(1.66053886e-27, "kg"),   # dalton
	"ua"  : Unit(1.495978706916e11, "m"), # astronomical unit
	"bar" : Unit(1e5, "Pa"),              # bar
	"mbar" : Unit(100, "Pa"),             # millibar
	"atm" : Unit(101325, "Pa"),           # atmosphere
	"mmHg" : Unit(133.322387415, "Pa"),   # mm of mercury at 0C
	"Torr" : Unit(101325/760, "Pa"),      # torr
	"th"  : Unit(0.0000254, "m"),         # thou (1/1000 inch)
	"in"  : Unit(0.0254, "m"),            # inches
	"ft"  : Unit(0.3048, "m"),            # feet
	"mi"  : Unit(1609.344, "m"),          # mile
	"gal" : Unit(0.0037854118, "m^3"),    # US gallon
}

for u in NON_SI_UNITS.keys():
	assert u not in UNITS, "symbol %s already exists in UNITS!" % u
	UNITS[u] = NON_SI_UNITS[u]
