"""
Test the bruktdel.no tracking functionality
"""
import unittest
import json
import os


class TestBruktdelTracking(unittest.TestCase):
    """Test bruktdel.no car parts tracking"""
    
    def test_tasks_module_imports(self):
        """Test that tasks module can be imported"""
        try:
            from assist import tasks
            self.assertTrue(hasattr(tasks, 'check_bruktdel_searches'))
            self.assertTrue(hasattr(tasks, 'check_bruktdel_listing'))
            self.assertTrue(hasattr(tasks, 'daily_marketplace_summary'))
        except ImportError as e:
            # Skip if frappe is not available (expected in non-Frappe environments)
            self.skipTest(f"Skipping: Frappe not available - {e}")
    
    def test_api_module_has_new_methods(self):
        """Test that API module has the new bruktdel methods"""
        try:
            from assist import api
            self.assertTrue(hasattr(api, 'save_bruktdel_search'))
            self.assertTrue(hasattr(api, 'get_car_assets'))
            self.assertTrue(hasattr(api, 'get_bruktdel_searches'))
            self.assertTrue(hasattr(api, 'trigger_bruktdel_check'))
        except ImportError as e:
            # Skip if frappe is not available (expected in non-Frappe environments)
            self.skipTest(f"Skipping: Frappe not available - {e}")
    
    def test_saved_marketplace_search_json_valid(self):
        """Test that the saved marketplace search JSON is valid"""
        import json
        json_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'assist_tools',
            'doctype',
            'saved_marketplace_search',
            'saved_marketplace_search.json'
        )
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Check that bruktdel.no is in the marketplace options
        marketplace_field = None
        for field in data.get('fields', []):
            if field.get('fieldname') == 'marketplace':
                marketplace_field = field
                break
        
        self.assertIsNotNone(marketplace_field, "Marketplace field not found")
        self.assertIn('bruktdel.no', marketplace_field.get('options', ''))
        
        # Check that asset_code field exists
        asset_code_field = None
        for field in data.get('fields', []):
            if field.get('fieldname') == 'asset_code':
                asset_code_field = field
                break
        
        self.assertIsNotNone(asset_code_field, "Asset code field not found")
        self.assertEqual(asset_code_field.get('fieldtype'), 'Link')
        self.assertEqual(asset_code_field.get('options'), 'Asset')
    
    def test_hooks_has_scheduler_events(self):
        """Test that hooks.py has scheduler events enabled"""
        hooks_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'hooks.py'
        )
        
        with open(hooks_path, 'r') as f:
            content = f.read()
        
        # Check that scheduler_events is not commented out
        self.assertIn('scheduler_events = {', content)
        self.assertIn('assist.tasks.check_bruktdel_searches', content)
        self.assertIn('assist.tasks.daily_marketplace_summary', content)


if __name__ == '__main__':
    unittest.main()
