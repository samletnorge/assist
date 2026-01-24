# Copyright (c) 2026, samletnorge and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from assist.assist_tools.doctype.marketplace_listing.marketplace_listing import generate_route_for_multiple_listings
import json


class TestMarketplaceListing(FrappeTestCase):
    def setUp(self):
        """Set up test data before each test."""
        # Clean up any existing test listings
        frappe.db.delete("Marketplace Listing", {"title": ["like", "Test%"]})
        frappe.db.commit()
    
    def tearDown(self):
        """Clean up test data after each test."""
        frappe.db.delete("Marketplace Listing", {"title": ["like", "Test%"]})
        frappe.db.commit()
    
    def test_gmaps_link_generation(self):
        """Test that Google Maps link is generated correctly for single listing."""
        listing = frappe.get_doc({
            "doctype": "Marketplace Listing",
            "listing_type": "Sale",
            "marketplace": "Facebook Marketplace",
            "title": "Test Item 1",
            "price": 100,
            "item_code": None,  # Optional for test
            "pickup_address": "Storgata 1",
            "pickup_city": "Oslo",
            "pickup_postal_code": "0001"
        })
        listing.insert(ignore_permissions=True)
        
        # Check that gmaps_route_link was generated
        self.assertIsNotNone(listing.gmaps_route_link)
        self.assertIn("https://www.google.com/maps/dir/", listing.gmaps_route_link)
        self.assertIn("Storgata+1", listing.gmaps_route_link)
        
        listing.delete()
    
    def test_gmaps_link_with_location_only(self):
        """Test Google Maps link generation with only pickup_location field."""
        listing = frappe.get_doc({
            "doctype": "Marketplace Listing",
            "listing_type": "Rental",
            "marketplace": "leid.no",
            "title": "Test Rental Item",
            "price": 500,
            "asset_code": None,  # Optional for test
            "pickup_location": "Lyngdal, Norway"
        })
        listing.insert(ignore_permissions=True)
        
        # Check that gmaps_route_link was generated
        self.assertIsNotNone(listing.gmaps_route_link)
        self.assertIn("Lyngdal", listing.gmaps_route_link)
        
        listing.delete()
    
    def test_no_gmaps_link_without_location(self):
        """Test that no Google Maps link is generated without location data."""
        listing = frappe.get_doc({
            "doctype": "Marketplace Listing",
            "listing_type": "Sale",
            "marketplace": "FINN.no",
            "title": "Test Item Without Location",
            "price": 200,
            "item_code": None
        })
        listing.insert(ignore_permissions=True)
        
        # Check that gmaps_route_link was not generated
        self.assertIsNone(listing.gmaps_route_link)
        
        listing.delete()
    
    def test_multiple_listings_route_generation(self):
        """Test route generation for multiple listings."""
        # Create multiple test listings
        listing1 = frappe.get_doc({
            "doctype": "Marketplace Listing",
            "listing_type": "Sale",
            "marketplace": "Facebook Marketplace",
            "title": "Test Multiple 1",
            "price": 100,
            "pickup_city": "Oslo",
            "pickup_postal_code": "0001"
        })
        listing1.insert(ignore_permissions=True)
        
        listing2 = frappe.get_doc({
            "doctype": "Marketplace Listing",
            "listing_type": "Sale",
            "marketplace": "Facebook Marketplace",
            "title": "Test Multiple 2",
            "price": 200,
            "pickup_city": "Bergen",
            "pickup_postal_code": "5000"
        })
        listing2.insert(ignore_permissions=True)
        
        # Generate route for multiple listings
        result = generate_route_for_multiple_listings(
            listing_ids=[listing1.name, listing2.name],
            start_location="Stavanger"
        )
        
        # Verify result
        self.assertTrue(result["success"])
        self.assertIn("route_link", result)
        self.assertEqual(result["total_stops"], 2)
        self.assertIn("Stavanger", result["route_link"])
        self.assertIn("Bergen", result["route_link"])
        
        listing1.delete()
        listing2.delete()
    
    def test_packaging_status_field(self):
        """Test that packaging status field works correctly."""
        listing = frappe.get_doc({
            "doctype": "Marketplace Listing",
            "listing_type": "Rental",
            "marketplace": "leid.no",
            "title": "Test Packaging Status",
            "price": 300,
            "packaging_status": "In Progress",
            "packaging_notes": "Need bubble wrap"
        })
        listing.insert(ignore_permissions=True)
        
        # Verify packaging fields
        self.assertEqual(listing.packaging_status, "In Progress")
        self.assertEqual(listing.packaging_notes, "Need bubble wrap")
        
        listing.delete()
    
    def test_auto_photoshoot_completed_flag(self):
        """Test that auto_photoshoot_completed flag works correctly."""
        listing = frappe.get_doc({
            "doctype": "Marketplace Listing",
            "listing_type": "Sale",
            "marketplace": "FINN.no",
            "title": "Test Photoshoot Flag",
            "price": 150,
            "auto_photoshoot_completed": 1
        })
        listing.insert(ignore_permissions=True)
        
        # Verify photoshoot flag
        self.assertEqual(listing.auto_photoshoot_completed, 1)
        
        listing.delete()

