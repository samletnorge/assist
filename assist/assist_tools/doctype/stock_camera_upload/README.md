# Stock Camera Upload Tool

## Overview

The Stock Camera Upload tool provides an intuitive way to add items to stock using phone camera images. It supports both single and batch upload modes with automatic image processing, background removal, and image enhancement.

## Features

✨ **Key Capabilities:**

- 📸 **Phone Camera Integration** - Capture items directly with your phone camera
- 🎨 **Automatic Background Removal** - AI-powered background removal for clean product images
- ✨ **Image Enhancement** - Automatic brightness, contrast, and sharpness optimization
- 📦 **Batch Processing** - Upload and process multiple items at once
- 🏪 **Warehouse Integration** - Automatically create stock entries in target warehouse
- 🤖 **AI Recognition** (Coming Soon) - Automatic item identification and categorization
- 📊 **Progress Tracking** - Real-time status updates for each image
- ⚡ **Fast & Efficient** - Process hundreds of items quickly

## Use Cases

1. **Warehouse Inventory** - Quickly photograph and add new inventory items
2. **Retail Stock** - Add products from phone photos during receiving
3. **Asset Management** - Document and track equipment with photos
4. **Field Operations** - Mobile workers can add items on-the-go
5. **Bulk Imports** - Process entire shipments by photographing items

## DocTypes

### Stock Camera Upload
Main document that manages the batch upload process.

**Fields:**
- `upload_name` - Descriptive name for the upload batch
- `warehouse` - Target warehouse for stock items
- `item_group` - Default item group classification
- `upload_mode` - Single or Batch mode
- `remove_background` - Enable automatic background removal
- `enhance_image` - Enable image enhancement
- `use_ai_recognition` - Enable AI-based item recognition (future)
- `auto_generate_item_code` - Automatically generate item codes
- `default_valuation_rate` - Default valuation for all items

**Child Tables:**
- `images` - List of uploaded camera images (Stock Camera Image)
- `items_created` - List of successfully created items (Stock Camera Created Item)

**Summary Fields:**
- `total_images` - Total number of images uploaded
- `total_items_created` - Number of successfully created items
- `failed_count` - Number of failed image processing attempts
- `processing_time` - Total processing time in seconds

### Stock Camera Image
Child table storing individual images and their processing status.

**Fields:**
- `image_file` - Attached image file
- `image_name` - Descriptive name for the image
- `status` - Processing status (Pending/Processing/Completed/Failed)
- `item_code` - Created item code (after processing)
- `error_message` - Error details if processing failed

### Stock Camera Created Item
Child table tracking successfully created items.

**Fields:**
- `item_code` - Link to created Item
- `item_name` - Name of the item
- `warehouse` - Warehouse where item was added
- `qty` - Quantity added (default: 1)
- `valuation_rate` - Valuation rate used
- `stock_entry` - Link to Stock Entry document
- `image_reference` - Reference to source image

## API Endpoints

### camera_batch_upload

Upload multiple items using phone camera images in batch mode.

```python
POST /api/method/assist.api.camera_batch_upload

{
    "images": ["base64_image_1", "base64_image_2", "base64_image_3"],
    "warehouse": "Main Warehouse",
    "upload_name": "Morning Receiving Batch",
    "item_group": "Products",
    "valuation_rate": 100.00,
    "remove_background": true,
    "enhance_image": true
}
```

**Response:**
```json
{
    "success": true,
    "upload_name": "UPLOAD-0001",
    "items_created": 3,
    "failed": 0,
    "processing_time": 12
}
```

### process_upload_batch

Process an existing Stock Camera Upload document.

```python
POST /api/method/assist.api.process_upload_batch

{
    "upload_name": "UPLOAD-0001"
}
```

**Response:**
```json
{
    "success": true,
    "total_images": 5,
    "items_created": 4,
    "failed": 1,
    "processing_time": 18
}
```

## MCP Server Tools

### batch_camera_upload_items

Add multiple items to stock using phone camera in batch mode via MCP protocol.

```python
from assist.mcp_server.server import batch_camera_upload_items

result = batch_camera_upload_items(
    images=[image1_base64, image2_base64, image3_base64],
    warehouse="Main Warehouse",
    upload_name="Batch Upload 2026-01-24",
    item_group="Raw Materials",
    valuation_rate=50.0,
    remove_background=True,
    enhance_image=True
)
```

## Usage Examples

### Example 1: Simple Batch Upload from Phone

```python
import frappe
import json
import base64

# Capture images with phone camera (base64 encoded)
images = [
    capture_from_camera(),  # Returns base64 image
    capture_from_camera(),
    capture_from_camera()
]

# Upload to stock
result = frappe.call(
    'assist.api.camera_batch_upload',
    images=json.dumps(images),
    warehouse='Main Warehouse',
    upload_name='Morning Inventory Check',
    remove_background=True,
    enhance_image=True
)

print(f"Created {result['items_created']} items")
```

### Example 2: Manual Upload Document

```python
import frappe

# Create upload document
upload = frappe.get_doc({
    "doctype": "Stock Camera Upload",
    "upload_name": "New Products Batch",
    "warehouse": "Main Warehouse",
    "item_group": "Products",
    "upload_mode": "Batch",
    "default_valuation_rate": 100.0,
    "remove_background": 1,
    "enhance_image": 1
})

# Add images
for image_file in image_files:
    upload.append("images", {
        "image_file": image_file,
        "image_name": f"Product {idx}",
        "status": "Pending"
    })

upload.insert()

# Process the batch
result = upload.process_all_images()
print(f"Processed: {result['items_created']} succeeded, {result['failed']} failed")
```

### Example 3: Using MCP Protocol

```python
from assist.mcp_server.server import batch_camera_upload_items

# Prepare images
images = load_images_from_folder("/path/to/photos")

# Upload via MCP
result = batch_camera_upload_items(
    images=images,
    warehouse="Warehouse - Seattle",
    upload_name="Seattle Shipment 2026-01-24",
    item_group="Electronics",
    valuation_rate=250.0,
    remove_background=True,
    enhance_image=True
)

if result["success"]:
    print(f"Success! Created {result['items_created']} items")
    print(f"Upload document: {result['upload_name']}")
else:
    print(f"Error: {result.get('error')}")
```

## Workflow

1. **Capture Images** - Use phone camera to photograph items
2. **Upload** - Send images via API or create upload document
3. **Processing** - System automatically:
   - Removes background from images
   - Enhances image quality
   - Generates unique item codes
   - Creates Item documents
   - Attaches processed images
   - Creates Stock Entries
4. **Review** - Check created items and fix any failures
5. **Complete** - Items are ready in stock

## Status Flow

```
Draft → Processing → Completed
                  → Failed
                  → Partially Completed
```

**Status Descriptions:**
- **Draft** - Upload created but not yet processed
- **Processing** - Currently processing images
- **Completed** - All images processed successfully
- **Failed** - All images failed to process
- **Partially Completed** - Some images succeeded, some failed

## Image Processing Pipeline

1. **Input** - Receive base64 encoded camera image
2. **Background Removal** (Optional)
   - Uses rembg library or altlokalt.com API
   - Removes distracting backgrounds
   - Creates clean product images
3. **Enhancement** (Optional)
   - Adjusts brightness (default: +10%)
   - Increases contrast (default: +10%)
   - Sharpens image (default: +20%)
4. **Storage** - Save processed image as File attachment
5. **Association** - Link image to Item document

## Configuration

### Image Processing Settings

Configure in Stock Camera Upload document:

- `remove_background` - Enable/disable background removal
- `enhance_image` - Enable/disable image enhancement
- `use_ai_recognition` - Enable AI item recognition (future)

### Default Settings

Set defaults in your code or API calls:

```python
DEFAULT_REMOVE_BG = True
DEFAULT_ENHANCE = True
DEFAULT_ITEM_GROUP = "All Item Groups"
DEFAULT_VALUATION = 0.0
```

## Performance

**Typical Processing Times:**
- Single image: 2-5 seconds
- 10 images batch: 20-50 seconds
- 100 images batch: 3-8 minutes

**Factors affecting speed:**
- Image size and resolution
- Background removal (adds 1-3 seconds per image)
- Image enhancement (adds 0.5-1 second per image)
- Network speed (if using external API)
- Server resources

## Troubleshooting

### Common Issues

**Issue: Images fail to process**
- Check image format (PNG, JPG supported)
- Ensure images are properly base64 encoded
- Verify rembg library is installed for background removal

**Issue: Items not created**
- Check warehouse exists and is active
- Verify item group is valid
- Check user permissions for Item creation

**Issue: Background removal fails**
- Install rembg: `pip install rembg`
- Or use altlokalt API by setting `use_altlokalt_api=True`

**Issue: Slow processing**
- Reduce image size before upload
- Disable background removal for faster processing
- Process in smaller batches

## Testing

Run the test suite:

```bash
# Run all tests
bench --site [site-name] run-tests assist.assist_tools.doctype.stock_camera_upload.test_stock_camera_upload

# Run specific test
bench --site [site-name] run-tests assist.assist_tools.doctype.stock_camera_upload.test_stock_camera_upload.TestStockCameraUpload.test_create_upload_document
```

## Future Enhancements

- 🤖 AI-powered item recognition and categorization
- 🏷️ Automatic barcode generation
- 📝 OCR for item names and details from images
- 🔍 Duplicate detection to prevent redundant items
- 📊 Analytics dashboard for upload statistics
- 🌐 Multi-language support for item names
- 🔄 Integration with supplier catalogs
- 📱 Native mobile app

## License

Copyright (c) 2026, samletnorge and contributors
For license information, please see license.txt

## Support

For issues or questions:
- GitHub Issues: https://github.com/samletnorge/assist/issues
- Documentation: See main README.md
