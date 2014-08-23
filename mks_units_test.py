#! /usr/bin/env python
# mks_units_test.py
#
# Copyright (c) 2014 Peter Hokanson
# Distributed under the terms of the MIT license (see LICENSE)
#

"""Unittests for mks_units."""

import random
import unittest
import math
from mks_units import Unit

class TestUnit(unittest.TestCase):
	def setUp(self):
		pass
	
	def test_init(self):
		my_units = []
		my_units.append(Unit(1, [1, 0, 0, 0, 0, 0, 0]))
		my_units.append(Unit(1, "kg m s^-2"))
		my_units.append(Unit(1, None))
		
	
	def test_format(self):
		my_unit = Unit(1.5, "kg m s^2 K^-1/2")

		# Check that we format the vector correctly
		self.assertEqual(my_unit.to_string("%d"),"1 kg m s^2 K^-1/2")
		self.assertEqual(my_unit.to_string("%1.1f"),"1.5 kg m s^2 K^-1/2")
		
		my_str = "{0:1.1f kg m s^2 K^-1/2}".format(my_unit)
		self.assertEqual(my_str, "1.5 kg m s^2 K^-1/2")
		my_str = "{0:1.1f g m s^2 K^-1/2}".format(my_unit)
		self.assertEqual(my_str, "1500.0 g m s^2 K^-1/2")
		
		my_str = "{0:1.1e g m ms^2 K^-1/2}".format(my_unit)
		self.assertEqual(my_str, "1.5e+09 g m ms^2 K^-1/2")
		
		my_str = "{0:3.3f}".format(my_unit)
		self.assertEqual(my_str, "1.500 kg m s^2 K^-1/2")
		
		# LaTeX formatting
		my_str = "{0:$3.3f}".format(my_unit)
		self.assertEqual(my_str, r"\SI{1.500}{ kg m s^{2} K^{-1/2}}")
		
		my_str = "{0:$1.1e g m ms^[2] K^[-1/2]}".format(my_unit)
		self.assertEqual(my_str, r"\SI{1.5e+09}{ g m ms^{2} K^{-1/2}}")
	
	def test_non_si(self):
		my_mpg = Unit(5, "mi gal^-1")
		
		my_str = "{0:1.3e m^-2}".format(my_mpg)
		self.assertEqual(my_str, "2.126e+06 m^-2")

	def test_lt_le_gt_ge(self):
		my_unit1 = Unit(1.5, "kg J C")
		my_unit2 = Unit(2.0, "kg J C")
		self.assertTrue(my_unit1 < my_unit2)
		self.assertFalse(my_unit2 < my_unit1)
		self.assertTrue(my_unit1 <= my_unit2)
		self.assertFalse(my_unit2 <= my_unit1)
		
		self.assertFalse(my_unit1 > my_unit2)
		self.assertTrue(my_unit2 > my_unit1)
		self.assertFalse(my_unit1 >= my_unit2)
		self.assertTrue(my_unit2 >= my_unit1)
		
		my_unitless = Unit(1.0, "")
		self.assertTrue(my_unitless < 5)
		self.assertFalse(my_unitless < 1)
		self.assertTrue(my_unitless <= 5)
		self.assertTrue(my_unitless <= 1)
		self.assertFalse(my_unitless <= 0.5)
		self.assertTrue(5 > my_unitless)
		self.assertFalse(1 > my_unitless)
		self.assertTrue(5 >= my_unitless)
		self.assertTrue(1 >= my_unitless)
		self.assertFalse(0.5 >= my_unitless)
	
	def test_add_sub(self):
		my_unit1 = Unit(1.0, "kg J C")
		my_unit2 = Unit(2.0, "kg J C")
		self.assertEqual(my_unit1 + my_unit1, my_unit2)
		self.assertEqual(my_unit2 + my_unit1, my_unit1 + my_unit2)
		
		my_unitless = Unit(1.0, "")
		self.assertEqual(my_unitless + 5, 6)
		self.assertEqual(my_unitless + 5, Unit(6, ""))
		self.assertEqual(5 + my_unitless, Unit(6, ""))
	
	def test_mul_div(self):
		my_unit1 = Unit(1.0, "m")
		my_unit2 = Unit(2.0, "s^-1")
		self.assertEqual(my_unit1 * my_unit2, Unit(2.0, "m s^-1"))
		self.assertEqual(my_unit2 * my_unit1, Unit(2.0, "m s^-1"))
		self.assertEqual(my_unit2 * 3, Unit(6.0, "s^-1"))
		
		self.assertEqual(my_unit1 / my_unit2, Unit(0.5, "m s"))
		self.assertEqual(my_unit2 / my_unit1, Unit(2, "m^-1 s^-1"))
		
		self.assertEqual(my_unit2 / 1, Unit(2, "s^-1"))
		self.assertEqual(1 / my_unit2, Unit(0.5, "s"))
	
	def test_pow(self):
		my_unit1 = Unit(4, "")
		my_unit2 = Unit(2, "K")
		
		self.assertEqual(my_unit2 ** 2, Unit(4, "K^2"))
		self.assertEqual(2 ** my_unit1, Unit(16, ""))
		self.assertEqual(my_unit2 ** my_unit1, Unit(16, "K^4"))
		self.assertEqual(my_unit1 ** my_unit1, Unit(256, ""))
	
	def test_float_int_complex_round(self):
		my_unit1 = Unit(4, "")
		my_unit2 = Unit(2, "K")
		
		self.assertEqual(float(my_unit1), float(4))
		self.assertEqual(float(my_unit2), float(2))
		
		self.assertEqual(int(my_unit1), int(4))
		self.assertEqual(int(my_unit2), int(2))
		
		self.assertEqual(complex(my_unit1), complex(4))
		self.assertEqual(complex(my_unit2), complex(2))
		
	def test_diode_equation(self):
		I_s = Unit(20e-9, "A")
		V_D = Unit(0.7, "V")
		T = Unit(270, "K")
		q = Unit(1.602e-19, "C")
		k = Unit(1.381e-23, "J K^-1")
		n = 1.6
		
		I_D = I_s * (math.e ** (V_D / (n * k * T / q)) - 1)
		#print(I_D)
		
	


if __name__ == '__main__':
	unittest.main(verbosity=2)