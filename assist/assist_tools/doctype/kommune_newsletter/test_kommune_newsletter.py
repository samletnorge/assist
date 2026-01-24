# Copyright (c) 2026, sm norge and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestKommuneNewsletter(FrappeTestCase):
	"""Test cases for Kommune Newsletter doctype."""
	
	def test_newsletter_creation(self):
		"""Test creating a basic newsletter entry."""
		newsletter = frappe.get_doc({
			"doctype": "Kommune Newsletter",
			"kommune": "Oslo",
			"newsletter_date": "2026-01-24",
			"title": "Nye støtteordninger for boligoppussing",
			"summary": "Oslo kommune lanserer nye støtteordninger for energieffektivisering",
			"category": "Building and Planning",
			"is_highlighted": 1
		})
		newsletter.insert()
		
		self.assertEqual(newsletter.kommune, "Oslo")
		self.assertTrue(newsletter.is_highlighted)
		
		# Clean up
		newsletter.delete()
