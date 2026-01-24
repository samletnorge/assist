# Copyright (c) 2026, sm norge and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
from frappe.utils import add_days, getdate


class GardenPlantingSchedule(Document):
    """Garden Planting Schedule for managing crop planting and harvesting"""
    
    def validate(self):
        """Calculate harvest dates and validate companion planting"""
        self.calculate_harvest_dates()
        self.check_companion_planting()
        
    def calculate_harvest_dates(self):
        """Calculate expected harvest dates based on crop maturity"""
        for item in self.planting_items:
            if item.crop and item.planting_date and not item.expected_harvest_date:
                crop = frappe.get_doc("Crop", item.crop)
                if crop.days_to_maturity:
                    item.expected_harvest_date = add_days(item.planting_date, crop.days_to_maturity)
    
    def check_companion_planting(self):
        """Check for companion planting conflicts and show warnings"""
        planted_crops = {}
        
        for item in self.planting_items:
            if item.crop:
                crop = frappe.get_doc("Crop", item.crop)
                planted_crops[item.crop] = crop
        
        # Check for bad companions
        warnings = []
        for crop_name, crop_doc in planted_crops.items():
            if crop_doc.bad_companions:
                bad_companions_list = [c.strip() for c in crop_doc.bad_companions.split(',')]
                for bad_companion in bad_companions_list:
                    if bad_companion in planted_crops:
                        warnings.append(
                            f"Warning: {crop_name} and {bad_companion} are incompatible companions"
                        )
        
        if warnings:
            frappe.msgprint(
                "<br>".join(warnings),
                title="Companion Planting Warnings",
                indicator="orange"
            )
    
    def get_planting_reminders(self):
        """Get list of upcoming planting reminders"""
        if not self.enable_email_reminders:
            return []
        
        reminders = []
        today = getdate()
        
        for item in self.planting_items:
            if item.planting_date and item.status == "Planned":
                days_until = (getdate(item.planting_date) - today).days
                if 0 < days_until <= self.reminder_days_before_planting:
                    reminders.append({
                        "type": "planting",
                        "crop": item.crop,
                        "variety": item.variety,
                        "date": item.planting_date,
                        "days_until": days_until
                    })
            
            if item.expected_harvest_date and item.status in ["Seeded/Planted", "Growing"]:
                days_until = (getdate(item.expected_harvest_date) - today).days
                if 0 < days_until <= self.reminder_days_before_harvest:
                    reminders.append({
                        "type": "harvest",
                        "crop": item.crop,
                        "variety": item.variety,
                        "date": item.expected_harvest_date,
                        "days_until": days_until
                    })
        
        return reminders
