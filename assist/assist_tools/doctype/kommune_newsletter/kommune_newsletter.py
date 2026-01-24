# Copyright (c) 2026, sm norge and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class KommuneNewsletter(Document):
	"""DocType for managing Kommune newsletter articles and announcements."""
	
	def validate(self):
		"""Validate the document before saving."""
		if not self.title or len(self.title.strip()) == 0:
			frappe.throw("Title is required")
	
	def before_save(self):
		"""Hook before saving the document."""
		# Auto-generate summary from content if not provided
		if not self.summary and self.full_content:
			# Extract first 200 characters of text content
			import re
			text_content = re.sub('<[^<]+?>', '', self.full_content)  # Remove HTML tags
			self.summary = text_content[:200] + "..." if len(text_content) > 200 else text_content
