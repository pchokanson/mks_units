#! /usr/bin/env python
# mks_units_test.py
#
# Copyright (c) 2014 Peter Hokanson
# Distributed under the terms of the MIT license (see LICENSE)
#

"""Unittests for mks_units."""

import random
import unittest
from mks_units import Unit

class TestUnit(unittest.TestCase):
	def setUp(self):
		pass
	
	def test_init(self):
		mass = Unit(1, [1, 0, 0, 0, 0, 0, 0])
		force = Unit(1, "kg m s^-2")
		my_unitless = Unit(1, None)
	
	def test_to_string(self):
		my_unit = Unit(1.5, "kg m s^2 K^-1/2")
		
		# Check that we format the vector correctly
		self.assertEqual(my_unit.to_string("%d"),"1 kg m s^2 K^-1/2")
		self.assertEqual(my_unit.to_string("%1.1f"),"1.5 kg m s^2 K^-1/2")

	def test_lt(self):
		my_unit1 = Unit(1.5, "kg J C")
		my_unit2 = Unit(2.0, "kg J C")
		self.assertTrue(my_unit1 < my_unit2)
		self.assertFalse(my_unit2 < my_unit1)
		
		my_unitless = Unit(1.0, "")
		self.assertTrue(my_unitless < 5)
		self.assertFalse(my_unitless < 1)
	
	def test_add(self):
		my_unit1 = Unit(1.0, "kg J C")
		my_unit2 = Unit(2.0, "kg J C")
		self.assertEqual(my_unit1 + my_unit1, my_unit2)
		
		my_unitless = Unit(1.0, "")
		self.assertEqual(my_unitless + 5, 6)
		self.assertEqual(my_unitless + 5, Unit(6, ""))


if __name__ == '__main__':
	unittest.main(verbosity=2)