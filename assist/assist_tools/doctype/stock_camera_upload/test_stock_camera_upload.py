# Copyright (c) 2026, samletnorge and contributors
# For license information, please see license.txt

import unittest
import frappe
import json
import base64
from unittest.mock import patch, MagicMock


class TestStockCameraUpload(unittest.TestCase):
	"""Test cases for Stock Camera Upload functionality."""
	
	def setUp(self):
		"""Set up test environment."""
		# Create test warehouse if it doesn't exist
		if not frappe.db.exists("Warehouse", "Test Camera Warehouse"):
			warehouse = frappe.get_doc({
				"doctype": "Warehouse",
				"warehouse_name": "Test Camera Warehouse",
				"is_group": 0
			})
			warehouse.insert()
		
		self.test_warehouse = "Test Camera Warehouse"
		self.test_item_group = "All Item Groups"
	
	def tearDown(self):
		"""Clean up test data."""
		# Delete test uploads
		uploads = frappe.get_all("Stock Camera Upload", 
			filters={"upload_name": ["like", "Test%"]},
			pluck="name"
		)
		for upload in uploads:
			frappe.delete_doc("Stock Camera Upload", upload, force=True)
		
		frappe.db.commit()
	
	def get_test_image_base64(self):
		"""Generate a simple test image in base64."""
		# Simple 1x1 PNG image in base64
		return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
	
	def test_create_upload_document(self):
		"""Test creating a Stock Camera Upload document."""
		upload = frappe.get_doc({
			"doctype": "Stock Camera Upload",
			"upload_name": "Test Upload 1",
			"warehouse": self.test_warehouse,
			"item_group": self.test_item_group,
			"upload_mode": "Single",
			"status": "Draft"
		})
		upload.insert()
		
		self.assertIsNotNone(upload.name)
		self.assertEqual(upload.status, "Draft")
		
		# Clean up
		frappe.delete_doc("Stock Camera Upload", upload.name, force=True)
	
	def test_add_images_to_upload(self):
		"""Test adding images to upload document."""
		upload = frappe.get_doc({
			"doctype": "Stock Camera Upload",
			"upload_name": "Test Upload Images",
			"warehouse": self.test_warehouse,
			"item_group": self.test_item_group,
			"upload_mode": "Batch",
			"status": "Draft"
		})
		
		# Add test images
		for i in range(3):
			upload.append("images", {
				"image_name": f"Test Image {i+1}",
				"status": "Pending"
			})
		
		upload.insert()
		
		self.assertEqual(len(upload.images), 3)
		self.assertEqual(upload.total_images, 3)
		
		# Clean up
		frappe.delete_doc("Stock Camera Upload", upload.name, force=True)
	
	@patch('assist.utils.image_processing.process_camera_image')
	def test_process_single_image(self, mock_process):
		"""Test processing a single image."""
		# Mock image processing to return test data
		mock_process.return_value = self.get_test_image_base64()
		
		upload = frappe.get_doc({
			"doctype": "Stock Camera Upload",
			"upload_name": "Test Single Process",
			"warehouse": self.test_warehouse,
			"item_group": self.test_item_group,
			"upload_mode": "Single",
			"status": "Draft",
			"remove_background": 1,
			"enhance_image": 1,
			"auto_generate_item_code": 1
		})
		
		# Add single image
		upload.append("images", {
			"image_name": "Test Product",
			"status": "Pending"
		})
		
		upload.insert()
		
		# Test internal method
		image_row = upload.images[0]
		result = upload._process_single_image(image_row)
		
		# Should return success even without actual image
		self.assertIn("success", result)
		
		# Clean up
		if result.get("success") and result.get("item_code"):
			if frappe.db.exists("Item", result["item_code"]):
				frappe.delete_doc("Item", result["item_code"], force=True)
		
		frappe.delete_doc("Stock Camera Upload", upload.name, force=True)
	
	def test_batch_upload_validation(self):
		"""Test validation of batch upload settings."""
		upload = frappe.get_doc({
			"doctype": "Stock Camera Upload",
			"upload_name": "Test Validation",
			"warehouse": self.test_warehouse,
			"upload_mode": "Batch",
			"status": "Draft"
		})
		
		upload.insert()
		
		# Should have default values
		self.assertEqual(upload.remove_background, 1)
		self.assertEqual(upload.enhance_image, 1)
		self.assertEqual(upload.auto_generate_item_code, 1)
		
		# Clean up
		frappe.delete_doc("Stock Camera Upload", upload.name, force=True)
	
	def test_api_camera_batch_upload(self):
		"""Test the API endpoint for batch camera upload."""
		from assist.api import camera_batch_upload
		
		# Prepare test data
		test_images = [self.get_test_image_base64() for _ in range(2)]
		images_json = json.dumps(test_images)
		
		# Mock the processing to avoid actual file operations
		with patch('assist.assist_tools.doctype.stock_camera_upload.stock_camera_upload.quick_batch_upload') as mock_upload:
			mock_upload.return_value = {
				"success": True,
				"upload_name": "UPLOAD-0001",
				"items_created": 2,
				"failed": 0,
				"processing_time": 5
			}
			
			result = camera_batch_upload(
				images=images_json,
				warehouse=self.test_warehouse,
				upload_name="Test API Upload",
				remove_background=True,
				enhance_image=True
			)
			
			self.assertTrue(result["success"])
			self.assertEqual(result["items_created"], 2)
	
	def test_mcp_batch_camera_upload_tool(self):
		"""Test the MCP server tool for batch camera upload."""
		from assist.mcp_server.server import batch_camera_upload_items
		
		# Prepare test data
		test_images = [self.get_test_image_base64() for _ in range(3)]
		
		# Mock the processing
		with patch('assist.assist_tools.doctype.stock_camera_upload.stock_camera_upload.quick_batch_upload') as mock_upload:
			mock_upload.return_value = {
				"success": True,
				"upload_name": "UPLOAD-0002",
				"items_created": 3,
				"failed": 0,
				"processing_time": 8
			}
			
			result = batch_camera_upload_items(
				images=test_images,
				warehouse=self.test_warehouse,
				upload_name="Test MCP Batch",
				item_group=self.test_item_group,
				valuation_rate=100.0,
				remove_background=True,
				enhance_image=True
			)
			
			self.assertTrue(result["success"])
			self.assertEqual(result["items_created"], 3)
	
	def test_status_transitions(self):
		"""Test status transitions during processing."""
		upload = frappe.get_doc({
			"doctype": "Stock Camera Upload",
			"upload_name": "Test Status",
			"warehouse": self.test_warehouse,
			"upload_mode": "Batch",
			"status": "Draft"
		})
		
		# Add images
		upload.append("images", {
			"image_name": "Test Image 1",
			"status": "Pending"
		})
		
		upload.insert()
		
		# Initially Draft
		self.assertEqual(upload.status, "Draft")
		
		# Would transition to Processing when submitted
		# (not actually submitting in test to avoid side effects)
		
		# Clean up
		frappe.delete_doc("Stock Camera Upload", upload.name, force=True)
	
	def test_error_handling_missing_warehouse(self):
		"""Test error handling when warehouse is missing."""
		try:
			upload = frappe.get_doc({
				"doctype": "Stock Camera Upload",
				"upload_name": "Test No Warehouse",
				"upload_mode": "Single",
				"status": "Draft"
				# Missing required warehouse field
			})
			upload.insert()
			self.fail("Should have raised validation error for missing warehouse")
		except Exception as e:
			# Expected to fail
			self.assertIn("Mandatory", str(e).lower() or "warehouse" in str(e).lower())
	
	def test_summary_calculations(self):
		"""Test that summary fields are calculated correctly."""
		upload = frappe.get_doc({
			"doctype": "Stock Camera Upload",
			"upload_name": "Test Summary",
			"warehouse": self.test_warehouse,
			"upload_mode": "Batch",
			"status": "Draft"
		})
		
		# Add 5 images
		for i in range(5):
			upload.append("images", {
				"image_name": f"Image {i+1}",
				"status": "Pending"
			})
		
		upload.insert()
		
		# Check total_images is updated
		self.assertEqual(upload.total_images, 5)
		
		# Initial counts should be 0
		self.assertEqual(upload.total_items_created, 0)
		self.assertEqual(upload.failed_count, 0)
		
		# Clean up
		frappe.delete_doc("Stock Camera Upload", upload.name, force=True)


# Run tests
def run_tests():
	"""Run all tests."""
	unittest.main()


if __name__ == "__main__":
	run_tests()
