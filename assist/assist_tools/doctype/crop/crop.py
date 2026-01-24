# Copyright (c) 2026, sm norge and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Crop(Document):
    """Crop master for farm season calendar"""
    
    def validate(self):
        """Validate crop data"""
        # Validate planting months
        if self.planting_start_month and self.planting_end_month:
            months = ["January", "February", "March", "April", "May", "June",
                     "July", "August", "September", "October", "November", "December"]
            start_idx = months.index(self.planting_start_month) if self.planting_start_month in months else -1
            end_idx = months.index(self.planting_end_month) if self.planting_end_month in months else -1
            
            # Check for invalid months
            if start_idx == -1 or end_idx == -1:
                frappe.throw("Invalid planting month specified")
            
            # Check if end is before start (may indicate year spanning)
            if start_idx > end_idx:
                frappe.msgprint(
                    "Planting end month is before start month. This may indicate a season that spans the new year.",
                    indicator="orange"
                )
