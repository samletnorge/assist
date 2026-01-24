# Copyright (c) 2026, sm norge and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestNorwegianSupportProgram(FrappeTestCase):
	"""Test cases for Norwegian Support Program doctype."""
	
	def test_program_creation(self):
		"""Test creating a basic support program."""
		program = frappe.get_doc({
			"doctype": "Norwegian Support Program",
			"program_name": "Test Enova Støtte",
			"provider": "Enova",
			"program_type": "Støtte",
			"category": "Energi",
			"status": "Active",
			"eligible_for_private_person": 1,
			"eligible_for_housing": 1
		})
		program.insert()
		
		self.assertEqual(program.program_name, "Test Enova Støtte")
		self.assertTrue(program.program_code)  # Should auto-generate
		
		# Clean up
		program.delete()
	
	def test_eligibility_validation(self):
		"""Test that at least one eligibility must be selected."""
		program = frappe.get_doc({
			"doctype": "Norwegian Support Program",
			"program_name": "Test Invalid Program",
			"provider": "Kommune",
			"program_type": "Støtte",
			"status": "Active"
		})
		
		with self.assertRaises(frappe.ValidationError):
			program.insert()
