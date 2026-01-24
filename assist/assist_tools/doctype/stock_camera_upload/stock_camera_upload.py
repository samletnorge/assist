# Copyright (c) 2026, samletnorge and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
import time
from typing import Dict, Any, List


class StockCameraUpload(Document):
	def validate(self):
		"""Validate the upload before saving."""
		if not self.created_by:
			self.created_by = frappe.session.user
		self.modified_by = frappe.session.user
		
		# Update total images count
		self.total_images = len(self.images)
	
	def before_submit(self):
		"""Process all images before submission."""
		if self.status == "Draft":
			self.status = "Processing"
	
	def on_submit(self):
		"""Process images and create items on submission."""
		self.process_all_images()
	
	def process_all_images(self):
		"""
		Process all uploaded images and create stock items.
		This is the main batch processing method.
		"""
		if not self.images:
			frappe.throw("No images uploaded to process")
		
		start_time = time.time()
		self.status = "Processing"
		self.save()
		frappe.db.commit()
		
		success_count = 0
		failed_count = 0
		
		for idx, image_row in enumerate(self.images):
			try:
				# Update image status
				image_row.status = "Processing"
				self.save()
				frappe.db.commit()
				
				# Process single image
				result = self._process_single_image(image_row)
				
				if result["success"]:
					image_row.status = "Completed"
					image_row.item_code = result["item_code"]
					
					# Add to created items table
					self.append("items_created", {
						"item_code": result["item_code"],
						"item_name": result.get("item_name"),
						"warehouse": self.warehouse,
						"qty": 1,
						"valuation_rate": result.get("valuation_rate", self.default_valuation_rate or 0),
						"stock_entry": result.get("stock_entry"),
						"image_reference": image_row.image_name or f"Image {idx + 1}"
					})
					
					success_count += 1
				else:
					image_row.status = "Failed"
					image_row.error_message = result.get("error", "Unknown error")
					failed_count += 1
				
				self.save()
				frappe.db.commit()
				
			except Exception as e:
				frappe.log_error(f"Error processing image {idx}: {str(e)}")
				image_row.status = "Failed"
				image_row.error_message = str(e)
				failed_count += 1
				self.save()
				frappe.db.commit()
		
		# Update summary
		end_time = time.time()
		self.processing_time = int(end_time - start_time)
		self.total_items_created = success_count
		self.failed_count = failed_count
		
		# Update final status
		if failed_count == 0:
			self.status = "Completed"
		elif success_count == 0:
			self.status = "Failed"
		else:
			self.status = "Partially Completed"
		
		self.save()
		frappe.db.commit()
		
		return {
			"success": True,
			"total_images": len(self.images),
			"items_created": success_count,
			"failed": failed_count,
			"processing_time": self.processing_time
		}
	
	def _process_single_image(self, image_row) -> Dict[str, Any]:
		"""
		Process a single image and create an item.
		
		Args:
			image_row: Row from the images child table
		
		Returns:
			Dictionary with processing result
		"""
		try:
			# Get image data
			image_data = self._get_image_data(image_row.image_file)
			
			if not image_data:
				return {
					"success": False,
					"error": "Could not load image data"
				}
			
			# Process image (remove background and enhance)
			if self.remove_background or self.enhance_image:
				try:
					from assist.utils.image_processing import process_camera_image
					
					processed_image = process_camera_image(
						image_data,
						remove_bg=self.remove_background,
						enhance=self.enhance_image,
						return_base64=True
					)
					image_data = processed_image
				except Exception as img_error:
					# Log error but continue with original image
					frappe.log_error(f"Image processing error: {str(img_error)}")
			
			# Generate item code
			if self.auto_generate_item_code:
				item_code = frappe.generate_hash(length=10).upper()
			else:
				# Try to use AI recognition if enabled
				item_code = frappe.generate_hash(length=10).upper()
			
			# Determine item name
			item_name = image_row.image_name or f"Camera Item {item_code}"
			
			# Create new item
			item = frappe.get_doc({
				"doctype": "Item",
				"item_code": item_code,
				"item_name": item_name,
				"item_group": self.item_group or "All Item Groups",
				"stock_uom": "Nos",
				"is_stock_item": 1,
				"description": f"Created from camera upload {self.name}"
			})
			
			# Attach processed image
			if image_data:
				try:
					file_doc = frappe.get_doc({
						"doctype": "File",
						"file_name": f"{item_code}_camera.png",
						"attached_to_doctype": "Item",
						"attached_to_name": item_code,
						"content": image_data if not image_data.startswith('data:') else image_data.split(',')[1],
						"is_private": 0
					})
					file_doc.insert()
					item.image = file_doc.file_url
				except Exception as file_error:
					frappe.log_error(f"Error attaching image: {str(file_error)}")
			
			item.insert()
			
			# Create stock entry to add to warehouse
			stock_entry = None
			if self.warehouse:
				stock_entry = frappe.get_doc({
					"doctype": "Stock Entry",
					"stock_entry_type": "Material Receipt",
					"to_warehouse": self.warehouse,
					"items": [{
						"item_code": item_code,
						"qty": 1,
						"basic_rate": self.default_valuation_rate or 0,
					}]
				})
				stock_entry.insert()
				stock_entry.submit()
			
			return {
				"success": True,
				"item_code": item_code,
				"item_name": item_name,
				"valuation_rate": self.default_valuation_rate or 0,
				"stock_entry": stock_entry.name if stock_entry else None
			}
			
		except Exception as e:
			frappe.log_error(f"Error processing image: {str(e)}")
			return {
				"success": False,
				"error": str(e)
			}
	
	def _get_image_data(self, image_file_url) -> str:
		"""
		Get base64 image data from file URL.
		
		Args:
			image_file_url: URL or path to the image file
		
		Returns:
			Base64 encoded image string
		"""
		try:
			import base64
			import requests
			from urllib.parse import urlparse
			
			# If it's already base64, return it
			if image_file_url and (image_file_url.startswith('data:image') or len(image_file_url) > 500):
				return image_file_url
			
			# Try to get file from Frappe
			if image_file_url:
				# Remove /files/ prefix if present
				file_path = image_file_url.replace('/files/', '')
				
				try:
					file_doc = frappe.get_doc("File", {"file_url": image_file_url})
					if file_doc.content:
						return file_doc.content
				except:
					pass
				
				# Try to read from site files
				try:
					site_path = frappe.get_site_path()
					full_path = f"{site_path}/public{image_file_url}"
					
					with open(full_path, 'rb') as f:
						image_bytes = f.read()
						return base64.b64encode(image_bytes).decode('utf-8')
				except:
					pass
			
			return None
			
		except Exception as e:
			frappe.log_error(f"Error getting image data: {str(e)}")
			return None


@frappe.whitelist()
def process_batch_upload(upload_name: str) -> Dict[str, Any]:
	"""
	Process a batch upload document.
	
	Args:
		upload_name: Name of the Stock Camera Upload document
	
	Returns:
		Processing result
	"""
	try:
		doc = frappe.get_doc("Stock Camera Upload", upload_name)
		result = doc.process_all_images()
		return result
	except Exception as e:
		frappe.log_error(f"Batch upload processing error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


@frappe.whitelist()
def quick_batch_upload(
	images: str,
	warehouse: str,
	upload_name: str = None,
	item_group: str = None,
	valuation_rate: float = None,
	remove_background: bool = True,
	enhance_image: bool = True
) -> Dict[str, Any]:
	"""
	Quick batch upload items from multiple camera images.
	
	Args:
		images: JSON array of base64 image strings
		warehouse: Target warehouse
		upload_name: Optional name for the upload
		item_group: Optional item group
		valuation_rate: Optional valuation rate
		remove_background: Whether to remove background
		enhance_image: Whether to enhance images
	
	Returns:
		Upload result with created items
	"""
	try:
		# Parse images
		if isinstance(images, str):
			images = json.loads(images)
		
		if not isinstance(images, list):
			return {
				"success": False,
				"error": "Images must be a list"
			}
		
		# Create upload document
		upload_doc = frappe.get_doc({
			"doctype": "Stock Camera Upload",
			"upload_name": upload_name or f"Batch Upload {frappe.utils.now()}",
			"warehouse": warehouse,
			"item_group": item_group or "All Item Groups",
			"upload_mode": "Batch",
			"default_valuation_rate": valuation_rate,
			"remove_background": 1 if remove_background else 0,
			"enhance_image": 1 if enhance_image else 0,
			"auto_generate_item_code": 1,
			"status": "Draft"
		})
		
		# Add images to child table
		for idx, img_data in enumerate(images):
			# Save image as file first
			file_doc = frappe.get_doc({
				"doctype": "File",
				"file_name": f"camera_image_{idx+1}_{frappe.generate_hash(length=6)}.png",
				"content": img_data if not img_data.startswith('data:') else img_data.split(',')[1],
				"is_private": 0
			})
			file_doc.insert()
			
			upload_doc.append("images", {
				"image_file": file_doc.file_url,
				"image_name": f"Image {idx + 1}",
				"status": "Pending"
			})
		
		upload_doc.insert()
		
		# Process immediately
		result = upload_doc.process_all_images()
		
		return {
			"success": True,
			"upload_name": upload_doc.name,
			"items_created": result.get("items_created", 0),
			"failed": result.get("failed", 0),
			"processing_time": result.get("processing_time", 0)
		}
		
	except Exception as e:
		frappe.log_error(f"Quick batch upload error: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}
