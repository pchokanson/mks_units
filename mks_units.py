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

#import types

class Unit(object):
	"""Unit type that stores a vector of SI base unit orders.  All SI-derived
	units are constructed as the product of powers of base units."""
	
	__slots__ = ["value", "units"]
	
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
	
	def __init__(self, value, units):
		"""Construct a Unit object with a given numeric value and unit type.  The
		type may either be given as a 7-element array or as a space-separated string
		of base and derived units with numeric powers.
		
		For the string formatting, SI units are separated by spaces and given
		exponents with the ^ operator.  """
		self.value = value
		
		if units is None:
			self.units = Unit.SI_UNITS[""]
		elif isinstance(units, (list, tuple)):
			# User has given us a direct list or tuple of our unit powers
			assert len(units) == 7, \
			       "Unexpected number of base unit terms in list %s" % units
			self.units = tuple([Fraction(i) for i in units])
		elif isinstance(units, str):
			self.units = self.string_to_unit_vector(units)
	
	def __repr__(self):
		return "Unit(%f, %s)" % (self.value, self.units)
	
	def __str__(self):
		return self.to_string()
	
	def to_string(self, formatstring="%f"):
		"""More option-ful string conversion function"""
		unit_string = ""
		for unit, power in zip(Unit.BASE_UNITS, self.units):
			if power == 0: # This unit isn't present
				pass 
			elif power == 1: # Implicit exponent
				unit_string += " %s" % unit
			elif isinstance(power, Fraction): # Fraction case
				unit_string += " %s^%s" % (unit, power)
			else: # Generic numeric
				unit_string += " %s^%f" % (unit, power)
		return (formatstring +"%s") % (self.value, unit_string)
	
	def to_LaTeX(self):
		return ""
	
	@staticmethod
	def string_to_unit_vector(unit_string):
		# Initial implementation won't handle SI prefixes
		
		# Accumulator begins dimensionless
		unit_vector = Unit.SI_UNITS[""]
		
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
			
			# Exponentiate this base unit
			this_unit_vector_base = Unit.SI_UNITS[base]
			this_unit_vector = Unit.pow_unit_vector(this_unit_vector_base, power)
			
			# Add to unit_vector accumulator
			unit_vector = Unit.mult_unit_vectors(unit_vector, this_unit_vector) 
		
		return unit_vector
	
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
			return Unit(n, "")
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
	
	def __sub__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		if self.match_units(other_unit):
			return Unit(self.value - other_unit.value, self.units)
		else: return NotImplemented
	
	def __mul__(self, other):
		other_unit = Unit.coerce_to_unit(other)
		new_unit_vector = Unit.mult_unit_vectors(self.units, other.units)
		return Unit(self.value * other.value, new_unit_vector)
	
	def __floordiv__(self, other):
		pass
	
	def __mod__(self, other):
		pass
	
	def __pow__(self, other):
		pass
	
	def __div__(self, other):
		pass
	
	def __truediv__(self, other):
		pass
	
	def __neg__(self):
		return Unit(-self.value, self.units)
	
	def __pos__(self):
		return Unit(-self.value, self.units)
	
	def __abs__(self):
		return Unit(abs(self.value), self.units)
	
	def __nonzero__(self):
		return bool(self.value)




