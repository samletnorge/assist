"""
Tests for Marketplace Hustle Routine
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class TestMarketplaceHustle(unittest.TestCase):
    """Test cases for marketplace hustle functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_search = {
            "name": "SMS-00001",
            "user": "test@example.com",
            "search_query": "byggningsmaterialer",
            "marketplace": "FINN.no",
            "search_type": "material_request",
            "last_checked": "2026-01-20 10:00:00"
        }
        
        self.sample_item = {
            "title": "Byggningsmaterialer - Paller",
            "price": "500 NOK",
            "url": "https://finn.no/item/12345",
            "marketplace": "FINN.no",
            "description": "Various building materials and pallets"
        }
    
    @patch('assist.utils.marketplace_hustle.frappe')
    def test_fetch_marketplace_items_returns_list(self, mock_frappe):
        """Test that fetch_marketplace_items returns a list"""
        from assist.utils.marketplace_hustle import fetch_marketplace_items
        
        result = fetch_marketplace_items("FINN.no", "paller", None)
        self.assertIsInstance(result, list)
    
    @patch('assist.utils.marketplace_hustle.frappe')
    def test_match_with_material_requests_no_matches(self, mock_frappe):
        """Test matching with Material Requests when no matches exist"""
        from assist.utils.marketplace_hustle import match_with_material_requests
        
        # Mock the database query to return empty list
        mock_frappe.db.sql.return_value = []
        
        result = match_with_material_requests(self.sample_item, "paller")
        self.assertFalse(result)
    
    @patch('assist.utils.marketplace_hustle.frappe')
    def test_match_with_tasks_no_matches(self, mock_frappe):
        """Test matching with Tasks when no matches exist"""
        from assist.utils.marketplace_hustle import match_with_tasks
        
        # Mock the database query to return empty list
        mock_frappe.db.sql.return_value = []
        
        result = match_with_tasks(self.sample_item, "paller")
        self.assertFalse(result)
    
    @patch('assist.utils.marketplace_hustle.frappe')
    def test_process_single_search(self, mock_frappe):
        """Test processing a single saved search"""
        from assist.utils.marketplace_hustle import process_single_search
        
        result = process_single_search(self.sample_search)
        
        self.assertIsInstance(result, dict)
        self.assertIn("items_found", result)
        self.assertIn("matches_created", result)
        self.assertIsInstance(result["items_found"], int)
        self.assertIsInstance(result["matches_created"], int)
    
    @patch('assist.utils.marketplace_hustle.frappe')
    def test_get_hustle_routine_status(self, mock_frappe):
        """Test getting hustle routine status"""
        from assist.utils.marketplace_hustle import get_hustle_routine_status
        
        # Mock database counts
        mock_frappe.db.count.side_effect = [10, 7]  # total, active
        mock_frappe.get_all.return_value = []
        
        result = get_hustle_routine_status()
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get("success"))
        self.assertIn("status", result)
    
    @patch('assist.utils.marketplace_hustle.frappe')
    def test_create_match_notification(self, mock_frappe):
        """Test creating a match notification"""
        from assist.utils.marketplace_hustle import create_match_notification
        
        # Mock frappe.get_doc to return a mock document
        mock_doc = MagicMock()
        mock_doc.owner = "test@example.com"
        mock_frappe.get_doc.side_effect = [MagicMock(), mock_doc]
        
        # Should not raise an exception
        create_match_notification(
            item=self.sample_item,
            reference_doctype="Material Request",
            reference_name="MAT-REQ-00001",
            match_type="material_request"
        )
        
        # Verify a comment was created
        self.assertTrue(mock_frappe.get_doc.called)


class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoint wrappers"""
    
    @patch('assist.api.frappe')
    def test_run_marketplace_hustle_routine_api(self, mock_frappe):
        """Test the API endpoint for running hustle routine"""
        # This would require a full frappe context, so we just verify the import
        try:
            from assist import api
            self.assertTrue(hasattr(api, 'run_marketplace_hustle_routine'))
        except ImportError:
            self.skipTest("Frappe not available for full API test")
    
    @patch('assist.api.frappe')
    def test_get_marketplace_hustle_status_api(self, mock_frappe):
        """Test the API endpoint for getting status"""
        try:
            from assist import api
            self.assertTrue(hasattr(api, 'get_marketplace_hustle_status'))
        except ImportError:
            self.skipTest("Frappe not available for full API test")


if __name__ == '__main__':
    unittest.main()
