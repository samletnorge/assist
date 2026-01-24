"""
API endpoints for Assist Tools

Provides whitelisted methods that can be called from the UI or external clients.
"""

import frappe
import json
from typing import Dict, Any


@frappe.whitelist()
def remove_image_background(image_data: str, enhance: bool = True, use_altlokalt_api: bool = False) -> Dict[str, Any]:
    """
    Remove background from an image.
    
    Args:
        image_data: Base64 encoded image data
        enhance: Whether to also enhance the image
        use_altlokalt_api: If True, uses receipt-ocr.altlokalt.com API
    
    Returns:
        Dictionary with processed image data
    """
    try:
        from assist.utils.image_processing import process_camera_image
        
        if isinstance(enhance, str):
            enhance = enhance.lower() == "true"
        if isinstance(use_altlokalt_api, str):
            use_altlokalt_api = use_altlokalt_api.lower() == "true"
        
        processed_image = process_camera_image(
            image_data,
            remove_bg=True,
            enhance=enhance,
            return_base64=True,
            use_altlokalt_api=use_altlokalt_api
        )
        
        return {
            "success": True,
            "processed_image": processed_image,
            "api_used": "altlokalt" if use_altlokalt_api else "rembg",
            "message": "Background removed successfully"
        }
    except Exception as e:
        frappe.log_error(f"Background removal error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to remove background"
        }


@frappe.whitelist()
def enhance_image(image_data: str, brightness: float = 1.1, contrast: float = 1.1, sharpness: float = 1.2) -> Dict[str, Any]:
    """
    Enhance image quality.
    
    Args:
        image_data: Base64 encoded image data
        brightness: Brightness factor (default 1.1)
        contrast: Contrast factor (default 1.1)
        sharpness: Sharpness factor (default 1.2)
    
    Returns:
        Dictionary with enhanced image data
    """
    try:
        from assist.utils.image_processing import enhance_image as enhance_img
        
        # Convert string parameters to float
        brightness = float(brightness)
        contrast = float(contrast)
        sharpness = float(sharpness)
        
        enhanced_image = enhance_img(
            image_data,
            enhance_brightness=brightness,
            enhance_contrast=contrast,
            enhance_sharpness=sharpness,
            return_base64=True
        )
        
        return {
            "success": True,
            "enhanced_image": enhanced_image,
            "message": "Image enhanced successfully"
        }
    except Exception as e:
        frappe.log_error(f"Image enhancement error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to enhance image"
        }


@frappe.whitelist()
def quick_add_item(
    image_data: str,
    warehouse: str,
    item_group: str = None,
    valuation_rate: float = None,
    remove_background: bool = True,
    enhance_image_quality: bool = True
) -> Dict[str, Any]:
    """
    Quick add item with camera image and automatic background removal.
    
    Args:
        image_data: Base64 encoded image data
        warehouse: Target warehouse
        item_group: Optional item group
        valuation_rate: Optional valuation rate
        remove_background: Whether to remove background
        enhance_image_quality: Whether to enhance image
    
    Returns:
        Dictionary with item creation result
    """
    try:
        from assist.mcp_server.server import quick_add_item_from_camera
        
        # Convert string booleans
        if isinstance(remove_background, str):
            remove_background = remove_background.lower() == "true"
        if isinstance(enhance_image_quality, str):
            enhance_image_quality = enhance_image_quality.lower() == "true"
        if valuation_rate:
            valuation_rate = float(valuation_rate)
        
        result = quick_add_item_from_camera(
            image_data=image_data,
            warehouse=warehouse,
            item_group=item_group,
            valuation_rate=valuation_rate,
            remove_background=remove_background,
            enhance_image=enhance_image_quality
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"Quick add item error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to add item"
        }


@frappe.whitelist()
def scan_receipt(
    receipt_image: str,
    add_as: str = "stock",
    warehouse: str = None,
    cost_center: str = None
) -> Dict[str, Any]:
    """
    Scan a receipt and add items automatically.
    
    Args:
        receipt_image: Base64 encoded receipt image
        add_as: Type to add items as ('stock' or 'asset')
        warehouse: Target warehouse for stock items
        cost_center: Cost center for asset items
    
    Returns:
        Dictionary with scan results
    """
    try:
        from assist.mcp_server.server import scan_receipt_and_add_items
        
        result = scan_receipt_and_add_items(
            receipt_image=receipt_image,
            add_as=add_as,
            warehouse=warehouse,
            cost_center=cost_center
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"Receipt scan error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to scan receipt"
        }


@frappe.whitelist()
def compare_prices(
    item_name: str,
    search_prisjakt: bool = True
) -> Dict[str, Any]:
    """
    Compare vendor prices for an item.
    
    Args:
        item_name: Name of item to search
        search_prisjakt: Whether to search Prisjakt.no
    
    Returns:
        Dictionary with price comparisons
    """
    try:
        from assist.mcp_server.server import compare_vendor_prices
        
        if isinstance(search_prisjakt, str):
            search_prisjakt = search_prisjakt.lower() == "true"
        
        result = compare_vendor_prices(
            item_name=item_name,
            search_prisjakt=search_prisjakt
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"Price comparison error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to compare prices"
        }


@frappe.whitelist()
def ask_inventory(query: str) -> Dict[str, Any]:
    """
    Ask a natural language question about inventory.
    
    Args:
        query: Natural language question
    
    Returns:
        Dictionary with answer
    """
    try:
        from assist.mcp_server.server import query_inventory_natural_language
        
        result = query_inventory_natural_language(query=query)
        
        return result
    except Exception as e:
        frappe.log_error(f"Inventory query error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to process query"
        }


@frappe.whitelist()
def plan_pickup_route(
    listings: str,
    start_location: str = None,
    preferred_date: str = None
) -> Dict[str, Any]:
    """
    Plan an optimized pickup route for marketplace listings.
    
    Args:
        listings: JSON string of listing IDs
        start_location: Starting location
        preferred_date: Preferred pickup date
    
    Returns:
        Dictionary with route plan
    """
    try:
        from assist.mcp_server.server import orchestrate_pickup_route
        import json
        
        listing_ids = json.loads(listings) if isinstance(listings, str) else listings
        
        result = orchestrate_pickup_route(
            listings=listing_ids,
            start_location=start_location,
            preferred_date=preferred_date
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"Pickup route error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to plan pickup route"
        }


@frappe.whitelist()
def generate_rds_designation(
    equipment_name: str,
    function_aspect: str = None,
    product_aspect: str = None,
    location_aspect: str = None,
    parent_system: str = None
) -> Dict[str, Any]:
    """
    Generate RDS 81346 reference designation for equipment.
    
    Args:
        equipment_name: Name of equipment
        function_aspect: Functional classification
        product_aspect: Product classification
        location_aspect: Location classification
        parent_system: Parent system designation
    
    Returns:
        Dictionary with RDS designation
    """
    try:
        from assist.mcp_server.server import generate_rds_81346_designation
        
        result = generate_rds_81346_designation(
            equipment_name=equipment_name,
            function_aspect=function_aspect,
            product_aspect=product_aspect,
            location_aspect=location_aspect,
            parent_system=parent_system
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"RDS designation error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate RDS designation"
        }


@frappe.whitelist()
def create_s1000d_module(
    item_code: str,
    data_module_code: str,
    title: str,
    content_type: str = "procedural",
    issue_number: str = "6"
) -> Dict[str, Any]:
    """
    Create S1000D Issue 6 data module for technical documentation.
    
    Args:
        item_code: ERPNext item code
        data_module_code: S1000D DMC
        title: Module title
        content_type: Content type
        issue_number: S1000D issue number
    
    Returns:
        Dictionary with data module structure
    """
    try:
        from assist.mcp_server.server import create_s1000d_data_module
        
        result = create_s1000d_data_module(
            item_code=item_code,
            data_module_code=data_module_code,
            title=title,
            content_type=content_type,
            issue_number=issue_number
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"S1000D module error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create S1000D module"
        }


@frappe.whitelist()
def import_github_repos(
    username: str = None,
    organization: str = None,
    github_token: str = None,
    import_as_assets: bool = True,
    asset_category: str = None
) -> Dict[str, Any]:
    """
    Import all GitHub repositories as assets in ERPNext.
    
    Args:
        username: GitHub username
        organization: GitHub organization name
        github_token: GitHub personal access token (optional)
        import_as_assets: Create as assets (True) or items only (False)
        asset_category: Asset category to assign
    
    Returns:
        Dictionary with import results
    """
    try:
        from assist.mcp_server.server import import_github_repos_as_assets
        
        if isinstance(import_as_assets, str):
            import_as_assets = import_as_assets.lower() == "true"
        
        result = import_github_repos_as_assets(
            username=username,
            organization=organization,
            github_token=github_token,
            import_as_assets=import_as_assets,
            asset_category=asset_category
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"GitHub import error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to import GitHub repositories"
        }


@frappe.whitelist()
def find_warehouses(
    location: str,
    search_query: str = "lager",
    region: str = None,
    add_to_erpnext: bool = True,
    phone_control: bool = False
) -> Dict[str, Any]:
    """
    Find warehouses on FINN.no in Norway (including northern regions).
    
    Args:
        location: Location to search (e.g., 'Tromsø', 'Bodø')
        search_query: Search query (default: 'lager')
        region: Optional region filter
        add_to_erpnext: Add found warehouses to ERPNext
        phone_control: Use phone control for automated browsing
    
    Returns:
        Dictionary with found warehouses
    """
    try:
        from assist.mcp_server.server import find_warehouses_on_finn
        
        if isinstance(add_to_erpnext, str):
            add_to_erpnext = add_to_erpnext.lower() == "true"
        if isinstance(phone_control, str):
            phone_control = phone_control.lower() == "true"
        
        result = find_warehouses_on_finn(
            location=location,
            search_query=search_query,
            region=region,
            add_to_erpnext=add_to_erpnext,
            phone_control=phone_control
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"Warehouse finder error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to find warehouses"
        }


@frappe.whitelist()
def manage_marketplace_with_phone(
    material_request_items: str = None,
    marketplace: str = "facebook",
    action: str = "search",
    message_template: str = "standard"
) -> Dict[str, Any]:
    """
    Manage marketplace listings with phone control and standard Norwegian messages.
    
    Args:
        material_request_items: JSON string of Material Request item IDs
        marketplace: Target marketplace ('facebook' or 'finn')
        action: Action to perform
        message_template: Message template to use
    
    Returns:
        Dictionary with marketplace management results
    """
    try:
        from assist.mcp_server.server import manage_marketplace_listings_with_phone_ctrl
        import json
        
        item_ids = json.loads(material_request_items) if material_request_items else None
        
        result = manage_marketplace_listings_with_phone_ctrl(
            material_request_items=item_ids,
            marketplace=marketplace,
            action=action,
            message_template=message_template
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"Marketplace management error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to manage marketplace listings"
        }


@frappe.whitelist()
def import_norwegian_accounts(standard: str = "NS4102", company: str = None) -> Dict[str, Any]:
    """
    Import Norwegian chart of accounts (NS 4102 or DFØ standard).
    
    Args:
        standard: "NS4102" for private sector or "DFO" for government sector
        company: Company name to import accounts for
    
    Returns:
        Dictionary with import results
    """
    try:
        from assist.mcp_server.server import import_norwegian_chart_of_accounts
        
        result = import_norwegian_chart_of_accounts(
            standard=standard,
            company=company
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"Norwegian accounts import error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to import Norwegian chart of accounts ({standard})"
        }


@frappe.whitelist()
def interact_with_skatteetaten(action: str, data: str = None) -> Dict[str, Any]:
    """
    Interact with Skatteetaten (Norwegian Tax Authority) API or via phone control.
    
    Args:
        action: Type of interaction (employee_registration, tax_report, deduction_request, check_deadlines, check_account)
        data: JSON string with additional data for the action
    
    Returns:
        Dictionary with interaction results
    """
    try:
        from assist.mcp_server.server import manage_skatteetaten_submissions
        import json
        
        data_dict = json.loads(data) if data else {}
        
        result = manage_skatteetaten_submissions(
            action=action,
            data=data_dict
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"Skatteetaten interaction error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to interact with Skatteetaten"
        }


@frappe.whitelist()
def submit_kommune_application(kommune: str, application_type: str, data: str = None) -> Dict[str, Any]:
    """
    Submit applications to Norwegian municipal services (kommune).
    
    Args:
        kommune: Municipality name (e.g., "Lyngdal")
        application_type: Type of application (building_permit, renovation_permit, property_upgrade)
        data: JSON string with application data
    
    Returns:
        Dictionary with submission results
    """
    try:
        from assist.mcp_server.server import submit_lyngdal_kommune_application
        import json
        
        data_dict = json.loads(data) if data else {}
        
        result = submit_lyngdal_kommune_application(
            kommune=kommune,
            application_type=application_type,
            data=data_dict
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"Kommune application error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to submit application to {kommune} Kommune"
        }


@frappe.whitelist()
def get_rental_assets(
    company: str = None,
    asset_category: str = None,
    chart_of_account_code: str = None
) -> Dict[str, Any]:
    """
    Get list of company-owned assets eligible for rental posting.
    
    Args:
        company: Company name (optional)
        asset_category: Filter by asset category (optional)
        chart_of_account_code: Filter by chart of account code (e.g., '1202', '1203', '1204')
    
    Returns:
        Dictionary with list of rental-eligible assets
    """
    try:
        from assist.mcp_server.server import get_rental_eligible_assets
        
        result = get_rental_eligible_assets(
            company=company,
            asset_category=asset_category,
            chart_of_account_code=chart_of_account_code
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"Get rental assets error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve rental-eligible assets"
        }


@frappe.whitelist()
def post_rental_listing(
    asset_code: str,
    marketplace: str,
    title: str,
    description: str,
    rental_rate: float,
    images: str = None
) -> Dict[str, Any]:
    """
    Post an asset to rental services like leid.no.
    
    Args:
        asset_code: Asset code to post
        marketplace: Target rental service
        title: Listing title
        description: Listing description
        rental_rate: Rental rate per period
        images: JSON string of image URLs
    
    Returns:
        Dictionary with posting result
    """
    try:
        from assist.mcp_server.server import post_asset_for_rental
        import json
        
        # Validate and convert rental_rate
        try:
            rental_rate = float(rental_rate)
            if rental_rate < 0:
                return {
                    "success": False,
                    "error": "rental_rate must be a positive number",
                    "message": "Invalid rental rate"
                }
        except (ValueError, TypeError) as e:
            return {
                "success": False,
                "error": f"Invalid rental_rate: {str(e)}",
                "message": "rental_rate must be a valid number"
            }
        
        # Validate and parse images
        image_list = None
        if images:
            try:
                image_list = json.loads(images)
                if not isinstance(image_list, list):
                    return {
                        "success": False,
                        "error": "images must be a JSON array",
                        "message": "Invalid images format"
                    }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Invalid JSON for images: {str(e)}",
                    "message": "images must be valid JSON array"
                }
        
        result = post_asset_for_rental(
            asset_code=asset_code,
            marketplace=marketplace,
            title=title,
            description=description,
            rental_rate=rental_rate,
            images=image_list
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"Post rental listing error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to post asset for rental"
        }


@frappe.whitelist()
def camera_batch_upload(
    images: str,
    warehouse: str,
    upload_name: str = None,
    item_group: str = None,
    valuation_rate: float = None,
    remove_background: bool = True,
    enhance_image: bool = True
) -> Dict[str, Any]:
    """
    Upload multiple items to stock using phone camera images in batch.
    Very intuitive for quickly adding many items to inventory.
    
    Args:
        images: JSON array of base64 encoded image strings
        warehouse: Target warehouse for stock items
        upload_name: Optional name for this batch upload
        item_group: Optional item group classification
        valuation_rate: Optional default valuation rate for all items
        remove_background: Automatically remove background from images
        enhance_image: Automatically enhance image quality
    
    Returns:
        Dictionary with batch upload results
    """
    try:
        from assist.assist_tools.doctype.stock_camera_upload.stock_camera_upload import quick_batch_upload
        
        # Convert string booleans
        if isinstance(remove_background, str):
            remove_background = remove_background.lower() == "true"
        if isinstance(enhance_image, str):
            enhance_image = enhance_image.lower() == "true"
        if valuation_rate:
            valuation_rate = float(valuation_rate)
        
        result = quick_batch_upload(
            images=images,
            warehouse=warehouse,
            upload_name=upload_name,
            item_group=item_group,
            valuation_rate=valuation_rate,
            remove_background=remove_background,
            enhance_image=enhance_image
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"Camera batch upload error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to process camera batch upload"
        }


@frappe.whitelist()
def process_upload_batch(upload_name: str) -> Dict[str, Any]:
    """
    Process an existing Stock Camera Upload batch.
    
    Args:
        upload_name: Name of the Stock Camera Upload document
    
    Returns:
        Processing result
    """
    try:
        from assist.assist_tools.doctype.stock_camera_upload.stock_camera_upload import process_batch_upload
        
        result = process_batch_upload(upload_name)
        return result
    except Exception as e:
        frappe.log_error(f"Process upload batch error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to process upload batch"
        }


@frappe.whitelist()
def save_bruktdel_search(search_query: str, asset_code: str = None, active: bool = True) -> Dict[str, Any]:
    """
    Save a new bruktdel.no search for tracking car parts.
    
    Args:
        search_query: The search term to look for on bruktdel.no
        asset_code: Optional asset code (car/vehicle) to link this search to
        active: Whether the search should be active (default: True)
    
    Returns:
        Dictionary with the created search record
    """
    try:
        # Convert string bool to actual bool
        if isinstance(active, str):
            active = active.lower() == "true"
        
        # Create the saved search
        doc = frappe.get_doc({
            "doctype": "Saved Marketplace Search",
            "user": frappe.session.user,
            "search_query": search_query,
            "marketplace": "bruktdel.no",
            "search_type": "purchase_request",
            "asset_code": asset_code,
            "active": active,
            "last_checked": None,  # Will be set when first check is performed
            "results_found": 0
        })
        doc.insert()
        frappe.db.commit()
        
        return {
            "success": True,
            "search_name": doc.name,
            "message": f"Saved bruktdel.no search for: {search_query}"
        }
    except Exception as e:
        frappe.log_error(f"Save bruktdel.no search error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to save bruktdel.no search"
        }


@frappe.whitelist()
def get_car_assets() -> Dict[str, Any]:
    """
    Get all car/vehicle assets from the system.
    
    This function retrieves assets that are transport vehicles (chart of account 1204)
    and suitable for tracking parts on bruktdel.no.
    
    Returns:
        Dictionary with list of car assets
    """
    try:
        # Get assets that are transport vehicles (account code 1204)
        # Based on the existing get_rental_eligible_assets pattern
        # Using broad category filter - can be made configurable via Site Config if needed
        assets = frappe.get_all(
            "Asset",
            filters={
                # Match categories containing "vehicle", "car", "transport", etc.
                # To customize, set 'car_asset_categories' in Site Config
                "asset_category": ["like", "%vehicle%"],
                "status": ["in", ["In Use", "Partially Depreciated", "Fully Depreciated"]]
            },
            fields=["name", "asset_name", "asset_category", "item_name", "status"],
            order_by="asset_name asc"
        )
        
        return {
            "success": True,
            "assets": assets,
            "count": len(assets)
        }
    except Exception as e:
        frappe.log_error(f"Get car assets error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get car assets"
        }


@frappe.whitelist()
def get_bruktdel_searches(asset_code: str = None, active_only: bool = True) -> Dict[str, Any]:
    """
    Get saved bruktdel.no searches, optionally filtered by asset.
    
    Args:
        asset_code: Optional asset code to filter searches
        active_only: If True, only return active searches (default: True)
    
    Returns:
        Dictionary with list of saved searches
    """
    try:
        # Convert string bool to actual bool
        if isinstance(active_only, str):
            active_only = active_only.lower() == "true"
        
        # Build filters
        filters = {
            "marketplace": "bruktdel.no"
        }
        
        if active_only:
            filters["active"] = 1
            
        if asset_code:
            filters["asset_code"] = asset_code
        
        # Get the searches
        searches = frappe.get_all(
            "Saved Marketplace Search",
            filters=filters,
            fields=["name", "search_query", "asset_code", "active", "last_checked", "results_found", "user"],
            order_by="last_checked desc"
        )
        
        return {
            "success": True,
            "searches": searches,
            "count": len(searches)
        }
    except Exception as e:
        frappe.log_error(f"Get bruktdel.no searches error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get bruktdel.no searches"
        }


@frappe.whitelist()
def trigger_bruktdel_check(search_name: str = None) -> Dict[str, Any]:
    """
    Manually trigger a check of bruktdel.no for a specific search or all active searches.
    
    Args:
        search_name: Optional specific search to check. If None, checks all active searches.
    
    Returns:
        Dictionary with check results
    """
    try:
        from assist.tasks import check_bruktdel_searches, check_bruktdel_listing
        
        if search_name:
            # Check a specific search
            search = frappe.get_doc("Saved Marketplace Search", search_name)
            
            if search.marketplace != "bruktdel.no":
                return {
                    "success": False,
                    "message": "Search is not for bruktdel.no marketplace"
                }
            
            results_count = check_bruktdel_listing(
                search_query=search.search_query,
                asset_code=search.asset_code,
                user=search.user
            )
            
            # Update the search record
            search.last_checked = frappe.utils.now()
            search.results_found = results_count
            search.save(ignore_permissions=True)
            frappe.db.commit()
            
            return {
                "success": True,
                "search_name": search_name,
                "results_found": results_count,
                "message": f"Checked bruktdel.no: {results_count} results found"
            }
        else:
            # Check all active searches
            check_bruktdel_searches()
            
            return {
                "success": True,
                "message": "Triggered check for all active bruktdel.no searches"
            }
            
    except Exception as e:
        frappe.log_error(f"Trigger bruktdel.no check error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to trigger bruktdel.no check"
        }

