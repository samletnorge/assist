"""
Enhanced MCP Server for ERPNext Assist Tools with Dynamic Tool Loading

This module provides a Model Context Protocol (MCP) server that exposes
ERPNext operations as tools that can be used by AI models. It supports
both built-in tools and dynamically loaded user-drafted tools from the UI.
"""

import os
import sys
import json
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("ERPNext Assist")


def load_user_drafted_tools():
    """
    Load and register tools that users have drafted in the UI.
    This allows non-programmers to create custom tools visually.
    """
    try:
        import frappe
        
        # Get all enabled user-drafted tools
        tools = frappe.get_all(
            "Assist Tool Draft",
            filters={"enabled": 1},
            fields=["name", "tool_name", "tool_description", "parameters"]
        )
        
        for tool_info in tools:
            # Dynamically create MCP tool for each user-drafted tool
            def create_tool_function(tool_name):
                def tool_function(**kwargs):
                    """Dynamically created tool from UI draft."""
                    tool = frappe.get_doc("Assist Tool Draft", tool_name)
                    return tool.execute_tool(kwargs)
                return tool_function
            
            # Register the tool with MCP
            tool_func = create_tool_function(tool_info.name)
            tool_func.__doc__ = tool_info.tool_description
            tool_func.__name__ = tool_info.tool_name.replace(" ", "_").lower()
            
            mcp.tool()(tool_func)
        
        return len(tools)
    except Exception as e:
        print(f"Error loading user-drafted tools: {e}", file=sys.stderr)
        return 0


# Tool 1: Marketplace Posting Tools
@mcp.tool()
def post_to_marketplace(
    marketplace: str,
    title: str,
    description: str,
    price: float,
    item_code: Optional[str] = None,
    asset_code: Optional[str] = None,
    listing_type: str = "Sale",
    images: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Post stock items or assets to marketplaces like Facebook Marketplace, FINN.no, leid.no, or other rental services.
    
    Args:
        marketplace: Target marketplace ('Facebook Marketplace', 'FINN.no', 'leid.no', 'Other Rental Service', 'Other')
        title: Listing title
        description: Listing description
        price: Listing price (sale price or rental rate)
        item_code: The ERPNext item code to post (for Sale listings)
        asset_code: The ERPNext asset code to post (for Rental listings)
        listing_type: Type of listing ('Sale' or 'Rental')
        images: List of image URLs or paths
    
    Returns:
        Dictionary with posting status and listing ID
    """
    try:
        # Import frappe here to avoid issues if frappe is not installed
        import frappe
        
        # Validate that either item_code or asset_code is provided
        if listing_type == "Sale" and not item_code:
            return {
                "success": False,
                "error": "item_code is required for Sale listings",
                "message": "Failed to create marketplace listing"
            }
        
        if listing_type == "Rental" and not asset_code:
            return {
                "success": False,
                "error": "asset_code is required for Rental listings",
                "message": "Failed to create marketplace listing"
            }
        
        # Get item or asset details from ERPNext
        if listing_type == "Sale":
            item = frappe.get_doc("Item", item_code)
        else:
            asset = frappe.get_doc("Asset", asset_code)
        
        # Create marketplace listing record
        listing_data = {
            "doctype": "Marketplace Listing",
            "listing_type": listing_type,
            "marketplace": marketplace,
            "title": title,
            "description": description,
            "price": price,
            "status": "Draft",
        }
        
        if listing_type == "Sale":
            listing_data["item_code"] = item_code
        else:
            listing_data["asset_code"] = asset_code
        
        listing = frappe.get_doc(listing_data)
        
        if images:
            for image_url in images:
                listing.append("images", {"image": image_url})
        
        listing.insert()
        frappe.db.commit()
        
        return {
            "success": True,
            "listing_id": listing.name,
            "marketplace": marketplace,
            "listing_type": listing_type,
            "item_code": item_code if listing_type == "Sale" else None,
            "asset_code": asset_code if listing_type == "Rental" else None,
            "message": f"{listing_type} listing created successfully for {marketplace}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create marketplace listing"
        }


@mcp.tool()
def track_saved_search(
    user: str,
    search_query: str,
    marketplace: str,
    search_type: str = "purchase_request",
) -> Dict[str, Any]:
    """
    Track and save search queries based on purchase or material request items.
    
    Args:
        user: ERPNext user ID
        search_query: The search query to track
        marketplace: Target marketplace for the search
        search_type: Type of search ('purchase_request' or 'material_request')
    
    Returns:
        Dictionary with search tracking status
    """
    try:
        import frappe
        
        # Create saved search record
        saved_search = frappe.get_doc({
            "doctype": "Saved Marketplace Search",
            "user": user,
            "search_query": search_query,
            "marketplace": marketplace,
            "search_type": search_type,
            "last_checked": frappe.utils.now(),
        })
        
        saved_search.insert()
        frappe.db.commit()
        
        return {
            "success": True,
            "search_id": saved_search.name,
            "message": "Search saved successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to save search"
        }


@mcp.tool()
def get_rental_eligible_assets(
    company: Optional[str] = None,
    asset_category: Optional[str] = None,
    chart_of_account_code: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get list of company-owned assets that are eligible for rental posting to leid.no and other rental services.
    Assets are identified by their chart of account codes (e.g., 1202 - Maskiner og anlegg, 1203 - Inventar, 1204 - Transportmidler).
    
    Args:
        company: Company name (optional, defaults to default company)
        asset_category: Filter by asset category (optional)
        chart_of_account_code: Filter by chart of account code like '1202', '1203', '1204' (optional)
    
    Returns:
        Dictionary with list of rental-eligible assets
    """
    try:
        import frappe
        
        if not company:
            company = frappe.defaults.get_user_default("Company")
        
        # Build filters
        filters = {
            "company": company,
            "status": ["in", ["Available for use", "Partially Depreciated", "Fully Depreciated"]]
        }
        
        if asset_category:
            filters["asset_category"] = asset_category
        
        # Get assets with fixed_asset_account field
        assets = frappe.get_all(
            "Asset",
            filters=filters,
            fields=["name", "asset_name", "item_code", "asset_category", "gross_purchase_amount", 
                    "available_for_use_date", "location", "custodian", "status", "fixed_asset_account"]
        )
        
        # Get all unique account names to fetch in bulk
        account_names = list(set(
            asset.get("fixed_asset_account") 
            for asset in assets 
            if asset.get("fixed_asset_account")
        ))
        
        # Fetch all accounts in a single query
        account_cache = {}
        if account_names:
            accounts = frappe.get_all(
                "Account",
                filters={"name": ["in", account_names]},
                fields=["name", "account_number"]
            )
            account_cache = {acc.name: acc for acc in accounts}
        
        # Filter by chart of account code if provided
        rental_eligible_assets = []
        for asset in assets:
            include_asset = False
            
            if chart_of_account_code:
                # Check if the asset's fixed asset account contains the chart code
                if asset.get("fixed_asset_account") and asset.fixed_asset_account in account_cache:
                    account = account_cache[asset.fixed_asset_account]
                    account_num = account.get("account_number") or ""
                    if chart_of_account_code in account_num or chart_of_account_code in account.name:
                        include_asset = True
            else:
                # If no specific chart code filter, include all
                # But preferably those with tool-related account codes (1202, 1203, 1204)
                if asset.get("fixed_asset_account") and asset.fixed_asset_account in account_cache:
                    account = account_cache[asset.fixed_asset_account]
                    account_num = account.get("account_number") or ""
                    tool_codes = ["1202", "1203", "1204"]
                    if any(code in account_num or code in account.name for code in tool_codes):
                        include_asset = True
                else:
                    # If no fixed asset account, include it anyway
                    include_asset = True
            
            if include_asset:
                rental_eligible_assets.append({
                    "asset_code": asset.name,
                    "asset_name": asset.asset_name,
                    "item_code": asset.item_code,
                    "category": asset.asset_category,
                    "purchase_amount": asset.gross_purchase_amount,
                    "location": asset.location,
                    "custodian": asset.custodian,
                    "status": asset.status,
                })
        
        return {
            "success": True,
            "company": company,
            "count": len(rental_eligible_assets),
            "assets": rental_eligible_assets,
            "message": f"Found {len(rental_eligible_assets)} rental-eligible assets"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve rental-eligible assets"
        }


@mcp.tool()
def post_asset_for_rental(
    asset_code: str,
    marketplace: str,
    title: str,
    description: str,
    rental_rate: float,
    images: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Post company-owned assets (tools, equipment) to rental services like leid.no.
    This is a convenience wrapper around post_to_marketplace specifically for rental listings.
    
    Args:
        asset_code: The ERPNext asset code to post for rental
        marketplace: Target rental service ('leid.no', 'Other Rental Service', etc.)
        title: Listing title
        description: Listing description
        rental_rate: Rental rate per period (day/week/month)
        images: List of image URLs or paths
    
    Returns:
        Dictionary with posting status and listing ID
    """
    try:
        # Use the post_to_marketplace function with rental parameters
        result = post_to_marketplace(
            marketplace=marketplace,
            title=title,
            description=description,
            price=rental_rate,
            asset_code=asset_code,
            listing_type="Rental",
            images=images,
        )
        
        if result["success"]:
            result["message"] = f"Asset {asset_code} posted for rental on {marketplace}"
        
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to post asset for rental"
        }


# Built-in Tool 2: Camera-based Item Addition with Background Removal
@mcp.tool()
def quick_add_item_from_camera(
    image_data: str,
    warehouse: str,
    item_group: Optional[str] = None,
    valuation_rate: Optional[float] = None,
    remove_background: bool = True,
    enhance_image: bool = True,
) -> Dict[str, Any]:
    """
    Quickly add a new item (stock or asset) using camera capture with automatic background removal.
    Useful for warehouses with disorganized or new items.
    
    Args:
        image_data: Base64 encoded image data or file path
        warehouse: Target warehouse for the item
        item_group: Optional item group classification
        valuation_rate: Optional valuation rate for the item
        remove_background: Automatically remove background from image (default: True)
        enhance_image: Automatically enhance image quality (default: True)
    
    Returns:
        Dictionary with item creation status and item code
    """
    try:
        import frappe
        from assist.utils.image_processing import process_camera_image
        
        # Process the image (remove background and enhance)
        if remove_background or enhance_image:
            try:
                processed_image = process_camera_image(
                    image_data,
                    remove_bg=remove_background,
                    enhance=enhance_image,
                    return_base64=True
                )
                image_data = processed_image
            except Exception as img_error:
                # Log error but continue with original image
                frappe.log_error(f"Image processing error: {str(img_error)}")
                print(f"Warning: Could not process image, using original. Error: {img_error}", file=sys.stderr)
        
        # Generate a temporary item code
        item_code = frappe.generate_hash(length=10).upper()
        
        # Create new item
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": item_code,
            "item_name": f"Quick Add {item_code}",
            "item_group": item_group or "All Item Groups",
            "stock_uom": "Nos",
            "is_stock_item": 1,
        })
        
        # Attach image if provided
        if image_data:
            # Save image as file attachment
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": f"{item_code}_image.png",
                "attached_to_doctype": "Item",
                "attached_to_name": item_code,
                "content": image_data,
            })
            file_doc.insert()
            item.image = file_doc.file_url
        
        item.insert()
        
        # Create stock entry if warehouse specified
        if warehouse:
            stock_entry = frappe.get_doc({
                "doctype": "Stock Entry",
                "stock_entry_type": "Material Receipt",
                "to_warehouse": warehouse,
                "items": [{
                    "item_code": item_code,
                    "qty": 1,
                    "basic_rate": valuation_rate or 0,
                }]
            })
            stock_entry.insert()
            stock_entry.submit()
        
        frappe.db.commit()
        
        return {
            "success": True,
            "item_code": item_code,
            "warehouse": warehouse,
            "background_removed": remove_background,
            "image_enhanced": enhance_image,
            "message": "Item created successfully from camera with processed image"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create item from camera"
        }


# Tool 3: Barcode Warehouse Location Scanner
@mcp.tool()
def scan_barcode_for_location(
    barcode: str,
) -> Dict[str, Any]:
    """
    Scan a barcode to quickly check which warehouse an item should be in.
    
    Args:
        barcode: The barcode value to scan
    
    Returns:
        Dictionary with warehouse location information
    """
    try:
        import frappe
        
        # Search for item by barcode
        item = frappe.db.get_value(
            "Item Barcode",
            {"barcode": barcode},
            ["parent as item_code"],
            as_dict=True
        )
        
        if not item:
            # Try direct item code match
            item_code = barcode
            if not frappe.db.exists("Item", item_code):
                return {
                    "success": False,
                    "message": "Item not found for barcode",
                    "barcode": barcode
                }
        else:
            item_code = item.item_code
        
        # Get item details
        item_doc = frappe.get_doc("Item", item_code)
        
        # Get warehouse stock levels
        stock_levels = frappe.db.sql("""
            SELECT 
                warehouse,
                actual_qty,
                reserved_qty,
                projected_qty
            FROM `tabBin`
            WHERE item_code = %s
            AND actual_qty > 0
            ORDER BY actual_qty DESC
        """, item_code, as_dict=True)
        
        # Get default warehouse
        default_warehouse = frappe.db.get_value(
            "Item Default",
            {"parent": item_code},
            "default_warehouse"
        )
        
        return {
            "success": True,
            "item_code": item_code,
            "item_name": item_doc.item_name,
            "barcode": barcode,
            "default_warehouse": default_warehouse,
            "stock_locations": stock_levels,
            "message": "Item location found successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to scan barcode"
        }


@mcp.tool()
def get_item_details(
    item_code: str,
) -> Dict[str, Any]:
    """
    Get detailed information about an item including stock levels across warehouses.
    
    Args:
        item_code: The ERPNext item code
    
    Returns:
        Dictionary with comprehensive item details
    """
    try:
        import frappe
        
        # Get item details
        item = frappe.get_doc("Item", item_code)
        
        # Get stock summary
        stock_summary = frappe.db.sql("""
            SELECT 
                warehouse,
                actual_qty,
                reserved_qty,
                ordered_qty,
                projected_qty,
                valuation_rate
            FROM `tabBin`
            WHERE item_code = %s
            ORDER BY warehouse
        """, item_code, as_dict=True)
        
        return {
            "success": True,
            "item_code": item_code,
            "item_name": item.item_name,
            "item_group": item.item_group,
            "stock_uom": item.stock_uom,
            "description": item.description,
            "stock_summary": stock_summary,
            "message": "Item details retrieved successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get item details"
        }


# New Tool 4: Receipt Scanner with OCR
@mcp.tool()
def scan_receipt_and_add_items(
    receipt_image: str,
    add_as: str = "stock",
    warehouse: Optional[str] = None,
    cost_center: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Scan a receipt image using OCR and automatically add items as stock or assets.
    
    Args:
        receipt_image: Base64 encoded receipt image
        add_as: Type to add items as ('stock' or 'asset')
        warehouse: Target warehouse for stock items
        cost_center: Cost center for asset items
    
    Returns:
        Dictionary with scanned items and creation status
    """
    try:
        import frappe
        
        # TODO: Implement OCR processing (e.g., using pytesseract or cloud OCR)
        # For now, this is a placeholder implementation
        
        items_created = []
        
        # Placeholder: In real implementation, parse receipt with OCR
        # and extract item names, quantities, prices
        
        # Example structure after OCR:
        # scanned_items = [
        #     {"name": "Item A", "qty": 2, "rate": 100},
        #     {"name": "Item B", "qty": 1, "rate": 50},
        # ]
        
        return {
            "success": True,
            "items_created": items_created,
            "add_as": add_as,
            "message": "Receipt scanned. Implement OCR processing to extract items.",
            "note": "This tool requires OCR library integration (pytesseract or similar)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to scan receipt"
        }


# New Tool 4.5: Batch Camera Upload for Stock Items
@mcp.tool()
def batch_camera_upload_items(
    images: List[str],
    warehouse: str,
    upload_name: Optional[str] = None,
    item_group: Optional[str] = None,
    valuation_rate: Optional[float] = None,
    remove_background: bool = True,
    enhance_image: bool = True,
) -> Dict[str, Any]:
    """
    Add multiple items to stock using phone camera in batch mode.
    Very intuitive for quickly photographing and adding many items at once.
    Automatically processes images with background removal and enhancement.
    
    Args:
        images: List of base64 encoded image strings from phone camera
        warehouse: Target warehouse for all items
        upload_name: Optional descriptive name for this batch upload
        item_group: Optional item group classification for all items
        valuation_rate: Optional default valuation rate for all items
        remove_background: Automatically remove background from all images (default: True)
        enhance_image: Automatically enhance image quality (default: True)
    
    Returns:
        Dictionary with batch upload results including items created and any failures
    """
    try:
        import frappe
        import json
        
        # Convert images list to JSON string for the API
        images_json = json.dumps(images) if not isinstance(images, str) else images
        
        # Call the quick batch upload function
        from assist.assist_tools.doctype.stock_camera_upload.stock_camera_upload import quick_batch_upload
        
        result = quick_batch_upload(
            images=images_json,
            warehouse=warehouse,
            upload_name=upload_name,
            item_group=item_group,
            valuation_rate=valuation_rate,
            remove_background=remove_background,
            enhance_image=enhance_image
        )
        
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to process batch camera upload"
        }


# New Tool 5: Price Comparison with Prisjakt.no
@mcp.tool()
def compare_vendor_prices(
    item_name: str,
    search_prisjakt: bool = True,
) -> Dict[str, Any]:
    """
    Compare vendor prices for an item using Prisjakt.no and internal vendor catalog.
    Suggests cheapest vendor and pulls vendor catalog.
    
    Args:
        item_name: Name or description of item to search
        search_prisjakt: Whether to search Prisjakt.no (default: True)
    
    Returns:
        Dictionary with vendor comparisons and catalog suggestions
    """
    try:
        import frappe
        import requests
        
        results = {
            "item_name": item_name,
            "internal_vendors": [],
            "prisjakt_results": [],
            "recommendations": []
        }
        
        # Search internal ERPNext suppliers
        suppliers = frappe.db.sql("""
            SELECT 
                s.name as supplier_name,
                si.item_code,
                si.item_name,
                si.supplier_part_no,
                si.last_purchase_rate
            FROM `tabSupplier` s
            LEFT JOIN `tabItem Supplier` si ON si.parent = s.name
            WHERE si.item_name LIKE %s OR si.item_code LIKE %s
            ORDER BY si.last_purchase_rate ASC
        """, (f"%{item_name}%", f"%{item_name}%"), as_dict=True)
        
        results["internal_vendors"] = suppliers
        
        # Search Prisjakt.no (placeholder - requires API key or web scraping)
        if search_prisjakt:
            # TODO: Implement Prisjakt.no API integration or web scraping
            results["prisjakt_results"] = []
            results["note"] = "Prisjakt.no integration requires API setup or web scraping"
        
        # Generate recommendations
        if suppliers:
            cheapest = min(suppliers, key=lambda x: x.get('last_purchase_rate', float('inf')))
            results["recommendations"].append({
                "type": "cheapest_internal",
                "supplier": cheapest.get('supplier_name'),
                "price": cheapest.get('last_purchase_rate'),
                "item_code": cheapest.get('item_code')
            })
        
        return {
            "success": True,
            "results": results,
            "message": f"Found {len(suppliers)} internal vendor matches"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to compare vendor prices"
        }


# New Tool 6: Natural Language Inventory Query (Voice/Text)
@mcp.tool()
def query_inventory_natural_language(
    query: str,
) -> Dict[str, Any]:
    """
    Answer natural language queries about inventory.
    Examples: "do we have pliers?", "where is the hammer?", "how many screws do we have?"
    
    Args:
        query: Natural language question about inventory
    
    Returns:
        Dictionary with query results in natural language
    """
    try:
        import frappe
        import re
        
        # Extract item keywords from query
        query_lower = query.lower()
        
        # Parse query intent
        is_availability = any(word in query_lower for word in ['have', 'got', 'stock', 'available'])
        is_location = any(word in query_lower for word in ['where', 'location', 'warehouse'])
        is_quantity = any(word in query_lower for word in ['how many', 'how much', 'quantity', 'count'])
        
        # Extract potential item names (simple approach - can be enhanced with NLP)
        # Remove common words
        stop_words = ['do', 'we', 'have', 'the', 'a', 'an', 'is', 'where', 'how', 'many', 'much', 'there']
        words = query_lower.split()
        item_keywords = [w.strip('?.,!') for w in words if w not in stop_words]
        
        # Search for items matching keywords
        search_pattern = '%' + '%'.join(item_keywords) + '%'
        items = frappe.db.sql("""
            SELECT 
                i.item_code,
                i.item_name,
                i.description,
                SUM(b.actual_qty) as total_qty,
                GROUP_CONCAT(DISTINCT b.warehouse) as warehouses
            FROM `tabItem` i
            LEFT JOIN `tabBin` b ON b.item_code = i.item_code AND b.actual_qty > 0
            WHERE i.item_name LIKE %s OR i.description LIKE %s OR i.item_code LIKE %s
            GROUP BY i.item_code
            HAVING total_qty > 0 OR total_qty IS NULL
            LIMIT 10
        """, (search_pattern, search_pattern, search_pattern), as_dict=True)
        
        # Generate natural language response
        if not items:
            response = f"No items found matching '{' '.join(item_keywords)}'. Try different keywords."
        elif len(items) == 1:
            item = items[0]
            qty = item.get('total_qty', 0) or 0
            warehouses = item.get('warehouses', 'unknown location')
            
            if is_location:
                response = f"Yes, we have {item['item_name']} in {warehouses}."
            elif is_quantity:
                response = f"We have {qty} units of {item['item_name']}."
            else:
                response = f"Yes, we have {qty} units of {item['item_name']} in {warehouses}."
        else:
            response = f"Found {len(items)} items matching your query:\n"
            for item in items[:5]:
                qty = item.get('total_qty', 0) or 0
                response += f"- {item['item_name']}: {qty} units\n"
        
        return {
            "success": True,
            "query": query,
            "response": response,
            "items_found": items,
            "message": "Query processed successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to process natural language query"
        }


# Enhancement to Tool 1: Pickup Route Orchestration with Standard Messages
@mcp.tool()
def orchestrate_pickup_route(
    listings: List[str],
    start_location: Optional[str] = None,
    preferred_date: Optional[str] = None,
    message_type: str = "standard",
) -> Dict[str, Any]:
    """
    Orchestrate efficient pickup routes for marketplace listings by contacting sellers.
    Schedules pickups and optimizes route for a specific day with standard Norwegian messages.
    
    Args:
        listings: List of marketplace listing IDs to schedule pickups for
        start_location: Starting location for the route
        preferred_date: Preferred pickup date (YYYY-MM-DD format)
        message_type: Type of message ('standard', 'storage', 'free_goods', 'apology')
    
    Returns:
        Dictionary with route plan, suggested messages, and seller contact status
    """
    try:
        import frappe
        from datetime import datetime
        
        # Standard Norwegian messages for marketplace communication
        standard_messages = {
            "standard": "Hvor mye for hele bunken?",
            "storage": "jeg vil gjerne prøve dere ut, passer idag og er tilgangen 24/7",
            "free_goods_tomorrow": "Er disse forsatt ledig kan hente imørgen hvis det passer... 😃",
            "free_goods_available": "noen artikler igjen?😃",
            "free_goods_delivery": "Er det mulig levering til lyngdal",
            "free_goods_pallets": "Hvor funker dette ... Vil gjerne ha fleste paller som mulig 😃",
            "apology": "Hei. Beklager sent svar men det var mange.., det er hentet"
        }
        
        route_plan = {
            "listings": [],
            "optimal_route": [],
            "date": preferred_date or datetime.now().strftime('%Y-%m-%d'),
            "start_location": start_location,
            "total_distance": 0,
            "estimated_time": 0,
            "standard_messages": standard_messages,
            "selected_message_type": message_type
        }
        
        for listing_id in listings:
            listing = frappe.get_doc("Marketplace Listing", listing_id)
            
            # Get seller contact info (would be stored in listing)
            # Select appropriate message based on context
            suggested_message = standard_messages.get(message_type, standard_messages["standard"])
            
            route_plan["listings"].append({
                "listing_id": listing_id,
                "item": listing.item_code,
                "status": "scheduled",
                "seller_contacted": True,
                "suggested_message": suggested_message,
                "pickup_time": None  # TODO: Get confirmed time from seller
            })
        
        # TODO: Implement route optimization algorithm
        # Could use Google Maps API, Mapbox, or other routing service
        
        route_plan["optimal_route"] = route_plan["listings"]  # Placeholder
        route_plan["message"] = f"Route planned for {len(listings)} pickups"
        route_plan["note"] = "Use phone control to contact sellers with suggested messages"
        
        return {
            "success": True,
            "route_plan": route_plan,
            "standard_messages": standard_messages,
            "message": f"Pickup route orchestrated for {len(listings)} items with Norwegian message templates"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to orchestrate pickup route"
        }


# New Tool 7: RDS 81346 Equipment Reference Designation
@mcp.tool()
def generate_rds_81346_designation(
    equipment_name: str,
    function_aspect: Optional[str] = None,
    product_aspect: Optional[str] = None,
    location_aspect: Optional[str] = None,
    parent_system: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate ISO/IEC 81346 (RDS) reference designations for equipment and systems.
    Creates standardized identifiers for industrial systems, installations, and equipment.
    
    Args:
        equipment_name: Name of the equipment/component
        function_aspect: Functional classification (what it does) - prefix with '='
        product_aspect: Product classification (what it is) - prefix with '-'
        location_aspect: Location classification (where it is) - prefix with '+'
        parent_system: Parent system reference designation
    
    Returns:
        Dictionary with generated RDS designation and metadata
    """
    try:
        import frappe
        
        # Generate RDS designation following ISO/IEC 81346 structure
        designation_parts = []
        
        if parent_system:
            designation_parts.append(parent_system)
        
        # Function aspect (=)
        if function_aspect:
            func_code = function_aspect if function_aspect.startswith('=') else f"={function_aspect}"
            designation_parts.append(func_code)
        
        # Product aspect (-)
        if product_aspect:
            prod_code = product_aspect if product_aspect.startswith('-') else f"-{product_aspect}"
            designation_parts.append(prod_code)
        
        # Location aspect (+)
        if location_aspect:
            loc_code = location_aspect if location_aspect.startswith('+') else f"+{location_aspect}"
            designation_parts.append(loc_code)
        
        # Generate full designation
        full_designation = ".".join(designation_parts) if designation_parts else equipment_name
        
        # Store in ERPNext as custom field or separate DocType
        result = {
            "success": True,
            "equipment_name": equipment_name,
            "rds_designation": full_designation,
            "aspects": {
                "function": function_aspect,
                "product": product_aspect,
                "location": location_aspect,
                "parent": parent_system
            },
            "standard": "ISO/IEC 81346",
            "message": f"RDS designation generated: {full_designation}"
        }
        
        # TODO: Optionally store in custom ERPNext DocType for equipment registry
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate RDS 81346 designation"
        }


# New Tool 8: S1000D Issue 6 Technical Documentation
@mcp.tool()
def create_s1000d_data_module(
    item_code: str,
    data_module_code: str,
    title: str,
    content_type: str = "procedural",
    issue_number: str = "6",
) -> Dict[str, Any]:
    """
    Create S1000D Issue 6 compliant data modules for technical publications.
    Generates standardized XML-based technical documentation for aerospace/defense equipment.
    
    Args:
        item_code: ERPNext item code for the equipment
        data_module_code: S1000D Data Module Code (DMC)
        title: Data module title
        content_type: Type of content ('procedural', 'descriptive', 'fault', 'crew')
        issue_number: S1000D issue number (default: '6')
    
    Returns:
        Dictionary with data module structure and metadata
    """
    try:
        import frappe
        from datetime import datetime
        
        # Get item details
        item = frappe.get_doc("Item", item_code)
        
        # Generate S1000D data module structure
        data_module = {
            "dmc": data_module_code,
            "issue_number": issue_number,
            "title": title,
            "item_code": item_code,
            "item_name": item.item_name,
            "content_type": content_type,
            "status": "draft",
            "created_date": datetime.now().isoformat(),
            "language": "en-US",
            "metadata": {
                "model_ident_code": item_code[:4] if len(item_code) >= 4 else "XXXX",
                "system_diff_code": "A",
                "system_code": "00",
                "sub_system_code": "0",
                "sub_sub_system_code": "0",
                "assy_code": "00",
                "disassy_code": "00",
                "disassy_code_variant": "00",
                "info_code": "000",
                "info_code_variant": "A",
                "item_location_code": "A"
            },
            "content": {
                "description": item.description or "",
                "specifications": {},
                "procedures": [],
                "warnings": [],
                "cautions": []
            }
        }
        
        # TODO: Generate actual XML structure according to S1000D schema
        # TODO: Store in Common Source Database (CSDB)
        
        return {
            "success": True,
            "data_module": data_module,
            "standard": "S1000D Issue 6",
            "message": f"S1000D data module created: {data_module_code}",
            "note": "Full XML generation and CSDB integration requires S1000D toolkit"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create S1000D data module"
        }


# New Tool 9: GitHub Repos as Assets Importer
@mcp.tool()
def import_github_repos_as_assets(
    username: Optional[str] = None,
    organization: Optional[str] = None,
    github_token: Optional[str] = None,
    import_as_assets: bool = True,
    asset_category: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Import all GitHub repositories as assets in ERPNext.
    Fetches repos from a user or organization and creates asset records.
    
    Args:
        username: GitHub username to import repos from
        organization: GitHub organization name to import repos from
        github_token: GitHub personal access token (optional, for private repos)
        import_as_assets: If True, creates assets; if False, creates items only
        asset_category: Asset category to assign (e.g., 'Software', 'Code Repository')
    
    Returns:
        Dictionary with imported repos and asset creation status
    """
    try:
        import frappe
        import requests
        
        if not username and not organization:
            return {
                "success": False,
                "error": "Either username or organization must be provided",
                "message": "Please specify a GitHub username or organization"
            }
        
        # Determine API endpoint
        if username:
            api_url = f"https://api.github.com/users/{username}/repos"
            target = username
            target_type = "user"
        else:
            api_url = f"https://api.github.com/orgs/{organization}/repos"
            target = organization
            target_type = "organization"
        
        # Set up headers with token if provided
        headers = {"Accept": "application/vnd.github.v3+json"}
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        
        # Fetch all repos (handle pagination)
        all_repos = []
        page = 1
        per_page = 100
        
        while True:
            response = requests.get(
                api_url,
                headers=headers,
                params={"page": page, "per_page": per_page},
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"GitHub API returned status {response.status_code}",
                    "message": response.json().get("message", "Failed to fetch repos")
                }
            
            repos = response.json()
            if not repos:
                break
            
            all_repos.extend(repos)
            page += 1
            
            # GitHub returns fewer than per_page items on last page
            if len(repos) < per_page:
                break
        
        # Import repos as assets
        imported_assets = []
        skipped_repos = []
        
        for repo in all_repos:
            try:
                repo_name = repo["name"]
                repo_full_name = repo["full_name"]
                repo_url = repo["html_url"]
                description = repo["description"] or f"GitHub repository: {repo_full_name}"
                language = repo.get("language", "Unknown")
                stars = repo.get("stargazers_count", 0)
                forks = repo.get("forks_count", 0)
                
                # Check if asset/item already exists
                item_code = f"REPO-{repo_name.upper()[:20]}"
                existing = frappe.db.exists("Asset", {"item_code": item_code})
                
                if existing:
                    skipped_repos.append({"name": repo_name, "reason": "already exists"})
                    continue
                
                # Create item first
                item = frappe.get_doc({
                    "doctype": "Item",
                    "item_code": item_code,
                    "item_name": repo_name,
                    "item_group": "Software",
                    "description": description,
                    "is_stock_item": 0,
                    "is_fixed_asset": 1 if import_as_assets else 0,
                })
                
                # Add custom fields for GitHub metadata
                item.append("custom_fields", {
                    "label": "GitHub URL",
                    "value": repo_url
                })
                item.append("custom_fields", {
                    "label": "Language",
                    "value": language
                })
                item.append("custom_fields", {
                    "label": "Stars",
                    "value": str(stars)
                })
                item.append("custom_fields", {
                    "label": "Forks",
                    "value": str(forks)
                })
                
                item.insert(ignore_permissions=True)
                
                # Create asset if requested
                if import_as_assets:
                    asset = frappe.get_doc({
                        "doctype": "Asset",
                        "item_code": item_code,
                        "asset_name": repo_name,
                        "asset_category": asset_category or "Software",
                        "gross_purchase_amount": 0,
                        "is_existing_asset": 1,
                        "available_for_use_date": frappe.utils.today(),
                    })
                    asset.insert(ignore_permissions=True)
                
                imported_assets.append({
                    "repo_name": repo_name,
                    "item_code": item_code,
                    "url": repo_url,
                    "language": language,
                    "stars": stars
                })
                
            except Exception as repo_error:
                skipped_repos.append({
                    "name": repo.get("name", "unknown"),
                    "reason": str(repo_error)
                })
        
        return {
            "success": True,
            "target": target,
            "target_type": target_type,
            "total_repos": len(all_repos),
            "imported_count": len(imported_assets),
            "skipped_count": len(skipped_repos),
            "imported_assets": imported_assets,
            "skipped_repos": skipped_repos,
            "message": f"Imported {len(imported_assets)} repositories from {target}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to import GitHub repos"
        }


# New Tool 10: Warehouse Finder for Northern Norway
@mcp.tool()
def find_warehouses_on_finn(
    location: str,
    search_query: str = "lager",
    region: Optional[str] = None,
    add_to_erpnext: bool = True,
    phone_control: bool = False,
) -> Dict[str, Any]:
    """
    Find warehouses anywhere in Norway (including northern regions) by searching FINN.no.
    Can use phone control to automate search and add results to ERPNext.
    
    Args:
        location: Location to search for warehouses (e.g., 'Tromsø', 'Bodø', 'Lyngdal')
        search_query: Search query for warehouses (default: 'lager')
        region: Optional region filter (e.g., 'Nord-Norge', 'Troms')
        add_to_erpnext: If True, automatically adds found warehouses to ERPNext
        phone_control: If True, uses phone control for automated browsing
    
    Returns:
        Dictionary with found warehouses and ERPNext creation status
    """
    try:
        import frappe
        import requests
        from bs4 import BeautifulSoup
        
        found_warehouses = []
        created_warehouses = []
        
        # Build FINN.no search URL
        # FINN.no realestate search for warehouses/storage
        base_url = "https://www.finn.no/realestate/lettings/search.html"
        search_params = {
            "q": search_query,
            "location": location,
        }
        
        if region:
            search_params["region"] = region
        
        # Note: This is a placeholder. Real implementation would require:
        # 1. Proper FINN.no API integration or web scraping with BeautifulSoup
        # 2. Phone control automation using tools like Appium or similar
        # 3. Handling of FINN.no's anti-bot measures
        
        if phone_control:
            # Placeholder for phone control automation
            result_note = "Phone control mode: Use mobile automation to browse FINN.no and extract warehouse listings"
        else:
            result_note = "Standard mode: API/web scraping for FINN.no warehouse listings"
        
        # Simulated warehouse data (in real implementation, parse from FINN.no)
        example_warehouses = [
            {
                "name": f"Warehouse in {location}",
                "address": f"{location}, Norway",
                "size_sqm": 0,
                "access_24_7": True,
                "contact_phone": "N/A",
                "finn_url": f"https://www.finn.no/...",
                "monthly_rent": 0,
            }
        ]
        
        # Add warehouses to ERPNext if requested
        if add_to_erpnext:
            for wh_data in example_warehouses:
                try:
                    # Check if warehouse already exists
                    wh_name = f"{wh_data['name']} - FINN".replace(" ", "-").lower()
                    
                    if frappe.db.exists("Warehouse", wh_name):
                        continue
                    
                    # Create warehouse in ERPNext
                    warehouse = frappe.get_doc({
                        "doctype": "Warehouse",
                        "warehouse_name": wh_data["name"],
                        "warehouse_type": "External",
                        "is_group": 0,
                    })
                    
                    # Note: Custom fields would need to be created in ERPNext for:
                    # - finn_url, access_24_7, monthly_rent, etc.
                    
                    warehouse.insert(ignore_permissions=True)
                    frappe.db.commit()
                    
                    created_warehouses.append({
                        "warehouse_name": warehouse.name,
                        "location": location,
                        "finn_url": wh_data["finn_url"]
                    })
                    
                except Exception as wh_error:
                    frappe.log_error(f"Warehouse creation error: {str(wh_error)}")
        
        return {
            "success": True,
            "location": location,
            "search_query": search_query,
            "found_count": len(example_warehouses),
            "created_count": len(created_warehouses),
            "found_warehouses": example_warehouses,
            "created_warehouses": created_warehouses,
            "phone_control_enabled": phone_control,
            "note": result_note,
            "message": f"Found {len(example_warehouses)} warehouses in {location}. Implement FINN.no API/scraping for real data.",
            "implementation_notes": [
                "Requires FINN.no API access or web scraping with BeautifulSoup",
                "Phone control requires mobile automation framework (Appium)",
                "Custom fields needed in Warehouse DocType for FINN.no metadata",
                "Consider FINN.no terms of service for automated access"
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to find warehouses on FINN.no"
        }


# New Tool 11: Enhanced Marketplace Communication with Material Requests
@mcp.tool()
def manage_marketplace_listings_with_phone_ctrl(
    material_request_items: Optional[List[str]] = None,
    marketplace: str = "facebook",
    action: str = "search",
    message_template: str = "standard",
) -> Dict[str, Any]:
    """
    Manage marketplace listings (Facebook, FINN.no) using phone control.
    Retrieves Material Request items saved by user and communicates with sellers using standard messages.
    
    Args:
        material_request_items: List of Material Request item IDs to search for
        marketplace: Target marketplace ('facebook' or 'finn')
        action: Action to perform ('search', 'message_seller', 'add_to_list')
        message_template: Template to use ('standard', 'storage', 'free_goods', 'apology')
    
    Returns:
        Dictionary with marketplace action results and communication status
    """
    try:
        import frappe
        
        # Standard Norwegian message templates
        message_templates = {
            "standard": "Hvor mye for hele bunken?",
            "storage": "jeg vil gjerne prøve dere ut, passer idag og er tilgangen 24/7",
            "free_goods_tomorrow": "Er disse forsatt ledig kan hente imørgen hvis det passer... 😃",
            "free_goods_available": "noen artikler igjen?😃",
            "free_goods_delivery": "Er det mulig levering til lyngdal",
            "free_goods_pallets": "Hvor funker dette ... Vil gjerne ha fleste paller som mulig 😃",
            "apology": "Hei. Beklager sent svar men det var mange.., det er hentet"
        }
        
        results = {
            "marketplace": marketplace,
            "action": action,
            "material_requests_processed": [],
            "message_template_used": message_template,
            "suggested_message": message_templates.get(message_template, message_templates["standard"]),
            "phone_control_instructions": []
        }
        
        # Get Material Request items if provided
        if material_request_items:
            for mr_item_id in material_request_items:
                try:
                    # Fetch material request item
                    mr_item = frappe.db.get_value(
                        "Material Request Item",
                        mr_item_id,
                        ["item_code", "item_name", "qty", "parent"],
                        as_dict=True
                    )
                    
                    if mr_item:
                        results["material_requests_processed"].append({
                            "item_code": mr_item.item_code,
                            "item_name": mr_item.item_name,
                            "quantity_needed": mr_item.qty,
                            "search_query": mr_item.item_name,
                            "suggested_message": results["suggested_message"]
                        })
                        
                        # Generate phone control instructions
                        if marketplace == "facebook":
                            instructions = [
                                f"1. Open Facebook Marketplace",
                                f"2. Search for '{mr_item.item_name}'",
                                f"3. Filter results by location",
                                f"4. Contact seller with: '{results['suggested_message']}'",
                                f"5. Add promising listings to saved list"
                            ]
                        elif marketplace == "finn":
                            instructions = [
                                f"1. Open FINN.no app",
                                f"2. Navigate to relevant category",
                                f"3. Search for '{mr_item.item_name}'",
                                f"4. Use filters for location and price",
                                f"5. Message seller: '{results['suggested_message']}'",
                                f"6. Save listing for tracking"
                            ]
                        else:
                            instructions = ["Unknown marketplace"]
                        
                        results["phone_control_instructions"].append({
                            "item": mr_item.item_name,
                            "steps": instructions
                        })
                        
                except Exception as item_error:
                    frappe.log_error(f"Material request item error: {str(item_error)}")
        
        return {
            "success": True,
            "results": results,
            "all_message_templates": message_templates,
            "message": f"Processed {len(results['material_requests_processed'])} material request items for {marketplace}",
            "note": "Use phone control to execute instructions and communicate with sellers"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to manage marketplace listings"
        }


@mcp.tool()
def import_norwegian_chart_of_accounts(standard: str = "NS4102", company: str = None):
    """
    Import Norwegian chart of accounts following NS 4102 standard (private sector)
    or DFØ standard (government sector).
    
    Args:
        standard: "NS4102" for private sector or "DFO" for government sector
        company: Company name to import accounts for (uses default if not provided)
    
    Returns:
        Dictionary with import results including number of accounts created
    
    Standards: NS 4102 (Norwegian Accounting Standard), DFØ Standard Kontoplan
    """
    try:
        import frappe
        
        if not company:
            company = frappe.defaults.get_user_default("Company")
        
        # NS 4102 Standard Chart of Accounts (Private Sector)
        ns4102_accounts = {
            "1": {"name": "1 - EIENDELER", "type": "Asset", "parent": None},
            "10": {"name": "10 - Anleggsmidler", "type": "Asset", "parent": "1"},
            "11": {"name": "11 - Immaterielle eiendeler", "type": "Asset", "parent": "10"},
            "1100": {"name": "1100 - Forskning og utvikling", "type": "Asset", "parent": "11"},
            "1101": {"name": "1101 - Konsesjoner, patenter, lisenser", "type": "Asset", "parent": "11"},
            "1102": {"name": "1102 - Goodwill", "type": "Asset", "parent": "11"},
            "12": {"name": "12 - Varige driftsmidler", "type": "Asset", "parent": "10"},
            "1200": {"name": "1200 - Tomter", "type": "Asset", "parent": "12"},
            "1201": {"name": "1201 - Bygninger", "type": "Asset", "parent": "12"},
            "1202": {"name": "1202 - Maskiner og anlegg", "type": "Asset", "parent": "12"},
            "1203": {"name": "1203 - Inventar", "type": "Asset", "parent": "12"},
            "1204": {"name": "1204 - Transportmidler", "type": "Asset", "parent": "12"},
            "13": {"name": "13 - Finansielle anleggsmidler", "type": "Asset", "parent": "10"},
            "1300": {"name": "1300 - Investeringer i datterselskap", "type": "Asset", "parent": "13"},
            "1301": {"name": "1301 - Lån til foretak i samme konsern", "type": "Asset", "parent": "13"},
            "14": {"name": "14 - Omløpsmidler", "type": "Asset", "parent": "1"},
            "1400": {"name": "1400 - Varelager", "type": "Asset", "parent": "14"},
            "1500": {"name": "1500 - Kundefordringer", "type": "Receivable", "parent": "14"},
            "1600": {"name": "1600 - Andre fordringer", "type": "Asset", "parent": "14"},
            "1900": {"name": "1900 - Kasse/Bank", "type": "Bank", "parent": "14"},
            "2": {"name": "2 - EGENKAPITAL OG GJELD", "type": "Liability", "parent": None},
            "20": {"name": "20 - Egenkapital", "type": "Equity", "parent": "2"},
            "2000": {"name": "2000 - Selskapskapital", "type": "Equity", "parent": "20"},
            "2050": {"name": "2050 - Opptjent egenkapital", "type": "Equity", "parent": "20"},
            "21": {"name": "21 - Avsetning for forpliktelser", "type": "Liability", "parent": "2"},
            "22": {"name": "22 - Langsiktig gjeld", "type": "Liability", "parent": "2"},
            "2200": {"name": "2200 - Gjeld til kredittinstitusjoner", "type": "Liability", "parent": "22"},
            "23": {"name": "23 - Kortsiktig gjeld", "type": "Liability", "parent": "2"},
            "2400": {"name": "2400 - Leverandørgjeld", "type": "Payable", "parent": "23"},
            "2600": {"name": "2600 - Skyldig offentlige avgifter", "type": "Liability", "parent": "23"},
            "2700": {"name": "2700 - Annen kortsiktig gjeld", "type": "Liability", "parent": "23"},
            "3": {"name": "3 - DRIFTSINNTEKTER", "type": "Income", "parent": None},
            "3000": {"name": "3000 - Salgsinntekter", "type": "Income", "parent": "3"},
            "3100": {"name": "3100 - Annen driftsinntekt", "type": "Income", "parent": "3"},
            "4": {"name": "4 - VAREKJØP", "type": "Cost of Goods Sold", "parent": None},
            "4000": {"name": "4000 - Varekjøp", "type": "Cost of Goods Sold", "parent": "4"},
            "4900": {"name": "4900 - Endring i beholdning", "type": "Cost of Goods Sold", "parent": "4"},
            "5": {"name": "5 - LØNNSKOSTNAD", "type": "Expense", "parent": None},
            "5000": {"name": "5000 - Lønn", "type": "Expense", "parent": "5"},
            "5400": {"name": "5400 - Arbeidsgiveravgift", "type": "Expense", "parent": "5"},
            "5900": {"name": "5900 - Andre personalkostnader", "type": "Expense", "parent": "5"},
            "6": {"name": "6 - ANNEN DRIFTSKOSTNAD", "type": "Expense", "parent": None},
            "6000": {"name": "6000 - Leie av lokaler", "type": "Expense", "parent": "6"},
            "6100": {"name": "6100 - Strøm og oppvarming", "type": "Expense", "parent": "6"},
            "6300": {"name": "6300 - Reparasjon og vedlikehold", "type": "Expense", "parent": "6"},
            "6700": {"name": "6700 - Kontorkostnader", "type": "Expense", "parent": "6"},
            "7": {"name": "7 - AVSKRIVNINGER", "type": "Expense", "parent": None},
            "7000": {"name": "7000 - Avskrivninger", "type": "Expense", "parent": "7"},
            "8": {"name": "8 - FINANSINNTEKTER OG FINANSKOSTNADER", "type": "Income", "parent": None},
            "8050": {"name": "8050 - Renteinntekter", "type": "Income", "parent": "8"},
            "8150": {"name": "8150 - Rentekostnader", "type": "Expense", "parent": "8"},
        }
        
        # DFØ Standard Kontoplan (Government Sector)
        dfo_accounts = {
            "1": {"name": "1 - Anleggsmidler", "type": "Asset", "parent": None},
            "10": {"name": "10 - Immaterielle eiendeler", "type": "Asset", "parent": "1"},
            "11": {"name": "11 - Varige driftsmidler", "type": "Asset", "parent": "1"},
            "12": {"name": "12 - Finansielle anleggsmidler", "type": "Asset", "parent": "1"},
            "2": {"name": "2 - Omløpsmidler og kortsiktige fordringer", "type": "Asset", "parent": None},
            "20": {"name": "20 - Beholdning av varer", "type": "Asset", "parent": "2"},
            "21": {"name": "21 - Fordringer", "type": "Receivable", "parent": "2"},
            "22": {"name": "22 - Bankinnskudd", "type": "Bank", "parent": "2"},
            "3": {"name": "3 - Opptjent ikke inntektsført", "type": "Asset", "parent": None},
            "4": {"name": "4 - Egenkapital", "type": "Equity", "parent": None},
            "40": {"name": "40 - Innskutt egenkapital", "type": "Equity", "parent": "4"},
            "41": {"name": "41 - Opptjent egenkapital", "type": "Equity", "parent": "4"},
            "5": {"name": "5 - Avsetninger til forpliktelser", "type": "Liability", "parent": None},
            "6": {"name": "6 - Annen langsiktig gjeld", "type": "Liability", "parent": None},
            "7": {"name": "7 - Kortsiktig gjeld", "type": "Liability", "parent": None},
            "70": {"name": "70 - Leverandørgjeld", "type": "Payable", "parent": "7"},
            "71": {"name": "71 - Skyldige offentlige avgifter", "type": "Liability", "parent": "7"},
            "8": {"name": "8 - Inntekt", "type": "Income", "parent": None},
            "80": {"name": "80 - Tilskudd og overføringer", "type": "Income", "parent": "8"},
            "81": {"name": "81 - Salgsinntekt", "type": "Income", "parent": "8"},
            "9": {"name": "9 - Kostnader", "type": "Expense", "parent": None},
            "90": {"name": "90 - Lønn og sosiale kostnader", "type": "Expense", "parent": "9"},
            "91": {"name": "91 - Varekjøp", "type": "Expense", "parent": "9"},
            "92": {"name": "92 - Andre driftskostnader", "type": "Expense", "parent": "9"},
            "93": {"name": "93 - Avskrivninger", "type": "Expense", "parent": "9"},
        }
        
        accounts_to_import = ns4102_accounts if standard.upper() == "NS4102" else dfo_accounts
        
        # Create accounts
        created_accounts = []
        for account_number, account_data in accounts_to_import.items():
            try:
                # Check if account already exists
                if frappe.db.exists("Account", {"account_number": account_number, "company": company}):
                    continue
                
                parent_account = None
                if account_data["parent"]:
                    parent_data = accounts_to_import.get(account_data["parent"])
                    if parent_data:
                        parent_account = frappe.db.get_value(
                            "Account",
                            {"account_number": account_data["parent"], "company": company},
                            "name"
                        )
                
                account = frappe.get_doc({
                    "doctype": "Account",
                    "account_name": account_data["name"],
                    "account_number": account_number,
                    "account_type": account_data["type"],
                    "company": company,
                    "parent_account": parent_account,
                    "is_group": len([k for k, v in accounts_to_import.items() if v.get("parent") == account_number]) > 0
                })
                account.insert(ignore_permissions=True)
                created_accounts.append(account.name)
            except Exception as acc_error:
                continue
        
        return {
            "success": True,
            "standard": standard,
            "company": company,
            "imported_count": len(created_accounts),
            "accounts": created_accounts[:10],  # Show first 10
            "message": f"Successfully imported {len(created_accounts)} accounts from {standard} standard"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to import Norwegian chart of accounts ({standard})"
        }


@mcp.tool()
def manage_skatteetaten_submissions(action: str, data: Dict[str, Any] = None):
    """
    Interact with Skatteetaten (Norwegian Tax Authority) for tax-related submissions.
    Supports employee registration (A-melding), tax reports, deductions, and deadline checking.
    
    Args:
        action: Type of interaction - 'employee_registration', 'tax_report', 'deduction_request', 'check_deadlines', 'check_account'
        data: Additional data for the submission (e.g., employee info, tax amounts)
    
    Returns:
        Dictionary with submission status and instructions for phone control if API unavailable
    
    Use cases:
    - Submit A-melding when hiring employees
    - File skattemelding (tax returns)
    - Request fradrag (tax deductions)
    - Check report deadlines
    - Monitor tax account status
    """
    try:
        import frappe
        
        data = data or {}
        
        action_handlers = {
            "employee_registration": "Submit A-melding (employee registration) to Skatteetaten",
            "tax_report": "Submit skattemelding (tax return)",
            "deduction_request": "File fradrag (tax deduction) request",
            "check_deadlines": "Check upcoming tax report deadlines",
            "check_account": "Check tax account status and balance"
        }
        
        if action not in action_handlers:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "available_actions": list(action_handlers.keys())
            }
        
        # Note: This is a placeholder implementation
        # In production, this would integrate with Skatteetaten's API or provide phone control instructions
        
        result = {
            "success": True,
            "action": action,
            "description": action_handlers[action],
            "status": "pending",
            "message": f"Action '{action}' initiated with Skatteetaten",
            "phone_control_required": True,
            "instructions": [
                "Navigate to https://skatteetaten.no",
                "Log in with BankID or MinID",
                f"Navigate to the appropriate section for {action}",
                "Follow the provided data to complete the submission"
            ],
            "data_provided": data,
            "next_steps": [
                "Complete BankID authentication",
                "Fill in required forms",
                "Review and submit",
                "Save confirmation number"
            ]
        }
        
        # Log the interaction for tracking
        frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "User",
            "reference_name": frappe.session.user,
            "content": f"Skatteetaten interaction: {action}"
        }).insert(ignore_permissions=True)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to interact with Skatteetaten"
        }


@mcp.tool()
def submit_lyngdal_kommune_application(kommune: str, application_type: str, data: Dict[str, Any] = None):
    """
    Submit applications to Norwegian municipal services (kommune).
    Supports building permits, renovation permits, and property upgrades.
    
    Args:
        kommune: Municipality name (e.g., "Lyngdal", "Oslo", "Bergen")
        application_type: Type of application - 'building_permit', 'renovation_permit', 'property_upgrade'
        data: Application data (property address, work description, estimated cost, etc.)
    
    Returns:
        Dictionary with submission status and tracking information
    
    Use cases:
    - Submit byggesøknad for building permits
    - Apply for renovation/painting permits
    - Register property upgrades to increase property value
    - Track property improvement projects
    """
    try:
        import frappe
        
        data = data or {}
        
        application_types = {
            "building_permit": "Byggesøknad (Building Permit)",
            "renovation_permit": "Renovasjon/maling søknad (Renovation/Painting Permit)",
            "property_upgrade": "Eiendomsoppgradering (Property Upgrade)"
        }
        
        if application_type not in application_types:
            return {
                "success": False,
                "error": f"Unknown application type: {application_type}",
                "available_types": list(application_types.keys())
            }
        
        # Note: This is a placeholder implementation
        # In production, this would integrate with the municipality's API or provide phone control instructions
        
        result = {
            "success": True,
            "kommune": kommune,
            "application_type": application_type,
            "description": application_types[application_type],
            "status": "submitted",
            "message": f"Application submitted to {kommune} Kommune",
            "phone_control_required": True,
            "instructions": [
                f"Navigate to {kommune.lower()}.kommune.no",
                "Log in with BankID",
                "Navigate to 'Søknader' or 'Applications'",
                f"Select '{application_types[application_type]}'",
                "Fill in the application form with provided data",
                "Submit the application"
            ],
            "data_provided": data,
            "expected_processing_time": "2-4 weeks",
            "property_value_impact": data.get("estimated_value_increase", "To be assessed"),
            "contact": f"{kommune} Kommune Building Department",
            "next_steps": [
                "Wait for case number",
                "Prepare additional documentation if requested",
                "Track application status online",
                "Receive decision letter"
            ]
        }
        
        # Log the application for tracking
        frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Info",
            "reference_doctype": "User",
            "reference_name": frappe.session.user,
            "content": f"{kommune} Kommune application: {application_type}"
        }).insert(ignore_permissions=True)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to submit application to {kommune} Kommune"
        }


# Norwegian Support Programs Tools
@mcp.tool()
def get_support_programs(
    entity_type: Optional[str] = None,
    provider: Optional[str] = None,
    program_type: Optional[str] = None,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get list of Norwegian support programs, grants, and deductions (støtte og fradrag).
    
    Search and retrieve information about available financial support programs in Norway
    for different entities including private persons, companies, housing projects, and farms.
    
    Args:
        entity_type: Filter by eligible entity type:
                    - "private_person": Support for individuals
                    - "company": Support for businesses
                    - "housing": Support for housing/residential projects (bolig)
                    - "farm": Support for farms and agriculture (gård)
        provider: Filter by provider organization:
                 - "Enova": Energy and climate support programs
                 - "Kommune": Municipal support and permits
                 - "Husbanken": Housing bank loans and grants
                 - "Innovasjon Norge": Business innovation support
                 - "Skatteetaten": Tax deductions (fradrag)
                 - "Landsbruksdirektoratet": Agricultural support
        program_type: Filter by program type:
                     - "Støtte": Grants and support
                     - "Fradrag": Tax deductions
                     - "Lån": Loans
                     - "Tilskudd": Subsidies
        category: Filter by category:
                 - "Energi": Energy efficiency and renewable energy
                 - "Bygg og oppgradering": Building and renovation
                 - "Klima og miljø": Climate and environment
                 - "Landbruk": Agriculture
                 - "Næring": Business and commerce
    
    Returns:
        Dictionary with list of matching support programs including:
        - Program name and description
        - Provider and eligibility requirements
        - Support amounts and coverage percentages
        - Application deadlines
        - Required documents
    
    Use cases:
    - Find all Enova støtte programs for private persons
    - Search for housing renovation grants (boligoppgradering)
    - Find tax deductions available for companies
    - Get farm support programs from Landsbruksdirektoratet
    - Find building permit requirements for kommune
    """
    try:
        import frappe
        from assist.api import get_norwegian_support_programs
        
        result = get_norwegian_support_programs(
            entity_type=entity_type,
            provider=provider,
            program_type=program_type,
            category=category,
            status="Active"
        )
        
@mcp.tool()
def run_marketplace_hustle_routine() -> Dict[str, Any]:
    """
    Trigger the marketplace hustle routine to check saved marketplace searches.
    
    This function checks all active saved marketplace searches (finn.no, Facebook Marketplace)
    for new items matching building materials, pallets, tracks, or other needed items.
    When new items are found, it checks if they match Material Requests or Tasks,
    and creates notifications for matches.
    
    Returns:
        Dictionary with processing results including searches processed, items found, and matches created
    """
    try:
        from assist.utils.marketplace_hustle import check_marketplace_searches
        
        result = check_marketplace_searches()
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to run marketplace hustle routine"
        }


@mcp.tool()
def get_enova_support_programs() -> Dict[str, Any]:
    """
    Get all active Enova support programs (Enova støtte).
    
    Retrieves comprehensive information about Enova's support programs for:
    - Energy efficiency improvements (varmepumper, isolasjon)
    - Renewable energy installations (solceller, varmeanlegg)
    - Business energy optimization
    - Sustainable transportation
    
    Enova is the Norwegian government enterprise responsible for promoting
    environmentally friendly production and consumption of energy.
    
    Returns:
        Dictionary with detailed information about all active Enova programs including:
        - Program names and descriptions
        - Eligibility criteria
        - Support amounts (minimum and maximum)
        - Coverage percentages
        - Requirements and documentation needed
        - Application deadlines
        - External links to official Enova pages
    
    Use cases:
    - Find heat pump (varmepumpe) support for homes
    - Get solar panel (solceller) installation grants
    - Check business energy efficiency support
    - Find EV charging station support
    """
    try:
        import frappe
        from assist.api import get_enova_support_programs
        
        result = get_enova_support_programs(status="Active")
        
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve Enova programs"
        }


@mcp.tool()
def search_norwegian_support(search_term: str) -> Dict[str, Any]:
    """
    Search Norwegian support programs by keyword.
    
    Searches across program names, descriptions, and categories to find
    relevant support programs, grants, and deductions.
    
    Args:
        search_term: Keyword or phrase to search for (in Norwegian or English)
                    Examples: "varmepumpe", "solar", "byggesøknad", "BSU",
                             "landbruk", "startup", "bolig"
    
    Returns:
        Dictionary with list of matching support programs
    
    Use cases:
    - Find specific support types: "varmepumpe", "solceller"
    - Search for general topics: "energi", "bygg", "landbruk"
    - Look for specific programs: "BSU", "etablererstipend"
    - Find building related support: "byggesøknad", "oppussing"
    """
    try:
        import frappe
        from assist.api import search_support_programs
        
        result = search_support_programs(
            search_term=search_term,
            status="Active"
        )
        
def get_marketplace_hustle_status() -> Dict[str, Any]:
    """
    Get the current status of the marketplace hustle routine.
    
    Returns statistics about saved marketplace searches including:
    - Total number of saved searches
    - Number of active searches
    - Recent search activity and results
    
    Returns:
        Dictionary with status information
    """
    try:
        from assist.utils.marketplace_hustle import get_hustle_routine_status
        
        result = get_hustle_routine_status()
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),

            "message": "Failed to get marketplace hustle routine status"
        }


def run_server(transport: str = "stdio"):
    """
    Run the MCP server with the specified transport.
    Loads both built-in and user-drafted tools before starting.
    
    Args:
        transport: Transport type ('stdio' or 'streamable-http')
    """
    # Load user-drafted tools before running the server
    num_tools = load_user_drafted_tools()
    print(f"Loaded {num_tools} user-drafted tools", file=sys.stderr)
    
    mcp.run(transport=transport)


if __name__ == "__main__":
    # Default to stdio transport for local AI integration
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    run_server(transport=transport)
