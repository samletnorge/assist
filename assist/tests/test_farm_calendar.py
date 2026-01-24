"""
Test the farm season calendar functionality
"""
import unittest
import json
import os


class TestFarmCalendar(unittest.TestCase):
    """Test farm season calendar features"""
    
    def test_crop_doctype_exists(self):
        """Test that Crop doctype JSON exists and is valid"""
        json_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'assist_tools',
            'doctype',
            'crop',
            'crop.json'
        )
        
        self.assertTrue(os.path.exists(json_path), "Crop doctype JSON not found")
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['name'], 'Crop')
        self.assertEqual(data['module'], 'Assist Tools')
        
        # Check key fields exist
        field_names = [field['fieldname'] for field in data['fields']]
        self.assertIn('crop_name', field_names)
        self.assertIn('crop_family', field_names)
        self.assertIn('norwegian_zone', field_names)
        self.assertIn('planting_start_month', field_names)
        self.assertIn('harvest_start_month', field_names)
        self.assertIn('days_to_maturity', field_names)
        self.assertIn('good_companions', field_names)
        self.assertIn('bad_companions', field_names)
    
    def test_garden_plot_doctype_exists(self):
        """Test that Garden Plot doctype JSON exists and is valid"""
        json_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'assist_tools',
            'doctype',
            'garden_plot',
            'garden_plot.json'
        )
        
        self.assertTrue(os.path.exists(json_path), "Garden Plot doctype JSON not found")
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['name'], 'Garden Plot')
        self.assertEqual(data['module'], 'Assist Tools')
        
        # Check key fields exist
        field_names = [field['fieldname'] for field in data['fields']]
        self.assertIn('plot_name', field_names)
        self.assertIn('norwegian_zone', field_names)
        self.assertIn('soil_type', field_names)
        self.assertIn('sun_exposure', field_names)
    
    def test_garden_planting_schedule_doctype_exists(self):
        """Test that Garden Planting Schedule doctype JSON exists and is valid"""
        json_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'assist_tools',
            'doctype',
            'garden_planting_schedule',
            'garden_planting_schedule.json'
        )
        
        self.assertTrue(os.path.exists(json_path), "Garden Planting Schedule doctype JSON not found")
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['name'], 'Garden Planting Schedule')
        self.assertEqual(data['module'], 'Assist Tools')
        
        # Check key fields exist
        field_names = [field['fieldname'] for field in data['fields']]
        self.assertIn('schedule_name', field_names)
        self.assertIn('garden_plot', field_names)
        self.assertIn('year', field_names)
        self.assertIn('planting_items', field_names)
        self.assertIn('enable_email_reminders', field_names)
        self.assertIn('reminder_email', field_names)
    
    def test_norwegian_crops_fixture_exists(self):
        """Test that Norwegian crops fixture exists and is valid"""
        fixture_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'fixtures',
            'norwegian_crops.json'
        )
        
        self.assertTrue(os.path.exists(fixture_path), "Norwegian crops fixture not found")
        
        with open(fixture_path, 'r') as f:
            crops = json.load(f)
        
        self.assertIsInstance(crops, list)
        self.assertGreater(len(crops), 0, "No crops in fixture")
        
        # Check first crop has required fields
        first_crop = crops[0]
        self.assertEqual(first_crop['doctype'], 'Crop')
        self.assertIn('crop_name', first_crop)
        self.assertIn('crop_family', first_crop)
        self.assertIn('norwegian_zone', first_crop)
        self.assertIn('planting_start_month', first_crop)
        
        # Check we have common Norwegian crops
        crop_names = [crop['crop_name'] for crop in crops]
        self.assertIn('Tomat (Tomato)', crop_names)
        self.assertIn('Gulrot (Carrot)', crop_names)
        self.assertIn('Potet (Potato)', crop_names)
    
    def test_api_module_has_farm_calendar_methods(self):
        """Test that API module has the new farm calendar methods"""
        try:
            from assist import api
            self.assertTrue(hasattr(api, 'get_planting_calendar'))
            self.assertTrue(hasattr(api, 'get_companion_planting_suggestions'))
            self.assertTrue(hasattr(api, 'get_crop_rotation_suggestions'))
            self.assertTrue(hasattr(api, 'calculate_succession_planting'))
            self.assertTrue(hasattr(api, 'generate_garden_shopping_list'))
            self.assertTrue(hasattr(api, 'get_upcoming_garden_tasks'))
        except ImportError as e:
            # Skip if frappe is not available (expected in non-Frappe environments)
            self.skipTest(f"Skipping: Frappe not available - {e}")
    
    def test_tasks_module_has_garden_reminders(self):
        """Test that tasks module has the garden reminders function"""
        try:
            from assist import tasks
            self.assertTrue(hasattr(tasks, 'send_garden_reminders'))
            self.assertTrue(hasattr(tasks, 'send_reminder_email'))
        except ImportError as e:
            # Skip if frappe is not available (expected in non-Frappe environments)
            self.skipTest(f"Skipping: Frappe not available - {e}")
    
    def test_hooks_has_garden_reminders_scheduler(self):
        """Test that hooks.py has the garden reminders scheduled task"""
        hooks_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'hooks.py'
        )
        
        with open(hooks_path, 'r') as f:
            content = f.read()
        
        # Check that scheduler_events includes garden reminders
        self.assertIn('scheduler_events = {', content)
        self.assertIn('assist.tasks.send_garden_reminders', content)
    
    def test_companion_planting_data_integrity(self):
        """Test that companion planting data has proper format"""
        fixture_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'fixtures',
            'norwegian_crops.json'
        )
        
        with open(fixture_path, 'r') as f:
            crops = json.load(f)
        
        for crop in crops:
            # Check companion data format
            if 'good_companions' in crop and crop['good_companions']:
                # Should be comma-separated string
                self.assertIsInstance(crop['good_companions'], str)
            
            if 'bad_companions' in crop and crop['bad_companions']:
                # Should be comma-separated string
                self.assertIsInstance(crop['bad_companions'], str)
    
    def test_norwegian_zone_values(self):
        """Test that Norwegian zone values are valid"""
        fixture_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'fixtures',
            'norwegian_crops.json'
        )
        
        with open(fixture_path, 'r') as f:
            crops = json.load(f)
        
        valid_zones = ['1', '2', '3', '4', '5', '6', '7', '8', 'All Zones']
        
        for crop in crops:
            if 'norwegian_zone' in crop:
                self.assertIn(crop['norwegian_zone'], valid_zones, 
                            f"Invalid zone for {crop['crop_name']}")


if __name__ == '__main__':
    unittest.main()
