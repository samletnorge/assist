# Copyright (c) 2026, samletnorge and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SavedMarketplaceSearch(Document):
    def validate(self):
        """Validate the saved search before saving."""
        if not self.last_checked:
            self.last_checked = frappe.utils.now()
