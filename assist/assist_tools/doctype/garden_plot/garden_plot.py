# Copyright (c) 2026, sm norge and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class GardenPlot(Document):
    """Garden Plot for managing planting areas"""
    
    def validate(self):
        """Calculate area if dimensions are provided"""
        if self.length_meters and self.width_meters:
            self.area_sqm = self.length_meters * self.width_meters
