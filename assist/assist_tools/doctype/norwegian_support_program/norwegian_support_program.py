# Copyright (c) 2026, sm norge and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class NorwegianSupportProgram(Document):
	"""DocType for managing Norwegian support programs, grants, and deductions."""
	
	def validate(self):
		"""Validate the document before saving."""
		# Ensure at least one eligibility checkbox is checked
		if not any([
			self.eligible_for_private_person,
			self.eligible_for_company,
			self.eligible_for_housing,
			self.eligible_for_farm
		]):
			frappe.throw("At least one eligibility type must be selected")
		
		# Validate amount ranges
		if self.support_amount_min and self.support_amount_max:
			if self.support_amount_min > self.support_amount_max:
				frappe.throw("Minimum support amount cannot be greater than maximum")
	
	def before_save(self):
		"""Hook before saving the document."""
		# Auto-generate program code if not provided
		if not self.program_code:
			self.program_code = self.generate_program_code()
	
	def generate_program_code(self):
		"""Generate a unique program code based on provider and name."""
		provider_code = self.provider[:3].upper() if self.provider else "XXX"
		# Get first 3 characters of program name
		name_code = "".join(filter(str.isalnum, self.program_name[:10])).upper()
		return f"{provider_code}-{name_code}"
