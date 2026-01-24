"""
API endpoints for Assist Tools

Provides whitelisted methods that can be called from the UI or external clients.
"""

import frappe
import json
from typing import Dict, Any


def _parse_bool(value):
    """
    Helper function to parse boolean values from string parameters.
    
    Args:
        value: Value to parse (can be bool, str, or other)
      `
    Returns:
        Boolean value
    """
    if isinstance(value, str):
        return value.lower() == "true"
    return bool(value)


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
        
        enhance = _parse_bool(enhance)
        use_altlokalt_api = _parse_bool(use_altlokalt_api)
        
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
        remove_background = _parse_bool(remove_background)
        enhance_image_quality = _parse_bool(enhance_image_quality)
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
        
        search_prisjakt = _parse_bool(search_prisjakt)
        
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
        
        import_as_assets = _parse_bool(import_as_assets)
        
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
        
        add_to_erpnext = _parse_bool(add_to_erpnext)
        phone_control = _parse_bool(phone_control)
        
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
        remove_background = _parse_bool(remove_background)
        enhance_image = _parse_bool(enhance_image)
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
def generate_marketplace_route(
    listing_ids: str,
    start_location: str = None
) -> Dict[str, Any]:
    """
    Generate a Google Maps route for multiple marketplace listings.
    Creates an optimized route with all pickup locations.
    
    Args:
        listing_ids: JSON array of Marketplace Listing IDs
        start_location: Optional starting location (address or place name)
    
    Returns:
        Dictionary with route link and listing details
    """
    try:
        from assist.assist_tools.doctype.marketplace_listing.marketplace_listing import generate_route_for_multiple_listings
        
        result = generate_route_for_multiple_listings(
            listing_ids=listing_ids,
            start_location=start_location
        )
        
        return result
    except Exception as e:
        frappe.log_error(f"Generate marketplace route error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate marketplace route"

def get_norwegian_support_programs(
    entity_type: str = None,
    provider: str = None,
    program_type: str = None,
    category: str = None,
    status: str = "Active"
) -> Dict[str, Any]:
    """
    Get list of Norwegian support programs (støtte og fradrag).
    
    Args:
        entity_type: Filter by eligibility - "private_person", "company", "housing", "farm"
        provider: Filter by provider (e.g., "Enova", "Kommune", "Skatteetaten")
        program_type: Filter by type - "Støtte", "Fradrag", "Lån", "Garantier", "Tilskudd"
        category: Filter by category (e.g., "Energi", "Bygg og oppgradering")
        status: Filter by status (default: "Active")
    
    Returns:
        Dictionary with list of matching support programs
    """
    try:
        filters = {}
        
        if status:
            filters["status"] = status
        if provider:
            filters["provider"] = provider
        if program_type:
            filters["program_type"] = program_type
        if category:
            filters["category"] = category
        
        # Add entity type filter if specified
        if entity_type:
            entity_field_map = {
                "private_person": "eligible_for_private_person",
                "company": "eligible_for_company",
                "housing": "eligible_for_housing",
                "farm": "eligible_for_farm"
            }
            if entity_type in entity_field_map:
                filters[entity_field_map[entity_type]] = 1
        
        programs = frappe.get_all(
            "Norwegian Support Program",
            filters=filters,
            fields=[
                "name", "program_name", "program_code", "provider", "program_type",
                "category", "status", "short_description", "external_url",
                "support_amount_min", "support_amount_max", "currency",
                "percentage_coverage", "application_deadline",
                "eligible_for_private_person", "eligible_for_company",
                "eligible_for_housing", "eligible_for_farm"
            ],
            order_by="program_name"
        )
        
        return {
            "success": True,
            "programs": programs,
            "count": len(programs),
            "filters_applied": filters,
            "message": f"Found {len(programs)} support programs"
        }
    except Exception as e:
        frappe.log_error(f"Get support programs error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve support programs"
        }


@frappe.whitelist()
def get_enova_support_programs(status: str = "Active") -> Dict[str, Any]:
    """
    Get all Enova support programs (Enova støtte).
    
    Args:
        status: Filter by status (default: "Active")
    
    Returns:
        Dictionary with list of Enova support programs
    """
    try:
        programs = frappe.get_all(
            "Norwegian Support Program",
            filters={
                "provider": "Enova",
                "status": status
            },
            fields=[
                "name", "program_name", "program_code", "program_type",
                "category", "short_description", "full_description", "external_url",
                "support_amount_min", "support_amount_max", "currency",
                "percentage_coverage", "application_deadline",
                "eligible_for_private_person", "eligible_for_company",
                "eligible_for_housing", "eligible_for_farm"
            ],
            order_by="program_name"
        )
        
        # Get detailed information for each program
        detailed_programs = []
        for prog in programs:
            program_doc = frappe.get_doc("Norwegian Support Program", prog.name)
            prog_dict = prog.as_dict()
            prog_dict["requirements"] = [r.as_dict() for r in program_doc.requirements]
            prog_dict["required_documents"] = [d.as_dict() for d in program_doc.required_documents]
            detailed_programs.append(prog_dict)
        
        return {
            "success": True,
            "programs": detailed_programs,
            "count": len(detailed_programs),
            "provider": "Enova",
            "message": f"Found {len(detailed_programs)} Enova support programs"
        }
    except Exception as e:
        frappe.log_error(f"Get Enova programs error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve Enova programs"
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
def run_marketplace_hustle_routine() -> Dict[str, Any]:
    """
    Manually trigger the marketplace hustle routine.
    
    This checks all active saved marketplace searches and matches new items
    with Material Requests and Tasks.
    
    Returns:
        Dictionary with processing results
    """
    try:
        from assist.utils.marketplace_hustle import check_marketplace_searches
        
        result = check_marketplace_searches()
        return result
    except Exception as e:
        frappe.log_error(f"Marketplace hustle routine error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to run marketplace hustle routine"         
        }


@frappe.whitelist()
def auto_photoshoot_rental_item(
    listing_id: str = None,
    asset_code: str = None,
    item_code: str = None,
    remove_background: bool = True,
    enhance_image: bool = True,
    num_angles: int = 4
) -> Dict[str, Any]:
    """
    Auto-capture multiple photos for a rental item or asset for marketplace listing.
    Can be used with existing listing or to create images for new listings.
    
    Args:
        listing_id: Existing Marketplace Listing ID (optional)
        asset_code: Asset code for rental items (optional)
        item_code: Item code for sale items (optional)
        remove_background: Automatically remove background from photos
        enhance_image: Enhance image quality
        num_angles: Number of different angles to capture (default: 4)
    
    Returns:
        Dictionary with photoshoot results and image URLs
    """
    try:
        # Convert string booleans
        remove_background = _parse_bool(remove_background)
        enhance_image = _parse_bool(enhance_image)
        
        if listing_id:
            # Update existing listing
            listing = frappe.get_doc("Marketplace Listing", listing_id)
            listing.auto_photoshoot_completed = 1
            listing.save()
            
            return {
                "success": True,
                "listing_id": listing_id,
                "message": f"Auto photoshoot marked as completed for listing {listing_id}",
                "note": "Use camera_batch_upload API to capture and process multiple angles",
                "recommended_angles": [
                    "Front view",
                    "Side view",
                    "Top view",
                    "Detail/close-up view"
                ]
            }
        
        return {
            "success": True,
            "message": "Auto photoshoot mode enabled",
            "instructions": [
                "1. Capture multiple photos from different angles",
                "2. Use camera_batch_upload API to process all images",
                "3. Create or update marketplace listing with processed images"
            ],
            "recommended_angles": num_angles,
            "settings": {
                "remove_background": remove_background,
                "enhance_image": enhance_image
            }
        }
    except Exception as e:
        frappe.log_error(f"Auto photoshoot error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to setup auto photoshoot"
        }
ef get_kommune_support_programs(kommune: str = None, status: str = "Active") -> Dict[str, Any]:
    """
    Get kommune (municipality) support programs.
    
    Args:
        kommune: Optional specific kommune name
        status: Filter by status (default: "Active")
    
    Returns:
        Dictionary with list of kommune support programs
    """
    try:
        filters = {
            "provider": "Kommune",
            "status": status
        }
        
        programs = frappe.get_all(
            "Norwegian Support Program",
            filters=filters,
            fields=[
                "name", "program_name", "program_code", "program_type",
                "category", "short_description", "external_url",
                "support_amount_min", "support_amount_max", "currency",
                "application_deadline",
                "eligible_for_private_person", "eligible_for_company",
                "eligible_for_housing", "eligible_for_farm"
            ],
            order_by="program_name"
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
            order_by="asset_name asc")
        
        return {
            "success": True,
            "programs": programs,
            "count": len(programs),
            "provider": "Kommune",
            "message": f"Found {len(programs)} kommune support programs"
        }
    except Exception as e:
        frappe.log_error(f"Get kommune programs error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve kommune programs"
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
def search_support_programs(search_term: str, status: str = "Active") -> Dict[str, Any]:
    """
    Search Norwegian support programs by keyword.
    
    Args:
        search_term: Keyword to search in program name and description
        status: Filter by status (default: "Active")
    
    Returns:
        Dictionary with list of matching support programs
    """
    try:
        # Search in program name and descriptions
        programs = frappe.db.sql("""
            SELECT 
                name, program_name, program_code, provider, program_type,
                category, status, short_description, external_url,
                support_amount_min, support_amount_max, currency,
                eligible_for_private_person, eligible_for_company,
                eligible_for_housing, eligible_for_farm
            FROM `tabNorwegian Support Program`
            WHERE status = %(status)s
            AND (
                program_name LIKE %(search)s
                OR short_description LIKE %(search)s
                OR full_description LIKE %(search)s
                OR category LIKE %(search)s
            )
            ORDER BY program_name
        """, {
            "status": status,
            "search": f"%{search_term}%"
        }, as_dict=True)
        
        return {
            "success": True,
            "programs": programs,
            "count": len(programs),
            "search_term": search_term,
            "message": f"Found {len(programs)} matching programs"
        }
    except Exception as e:
        frappe.log_error(f"Search support programs error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to search support programs"
        }
          
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
def get_kommune_newsletters(
    kommune: str = None,
    is_highlighted: bool = None,
    category: str = None,
    status: str = "Published",
    limit: int = 20
) -> Dict[str, Any]:
    """
    Get kommune newsletter articles and announcements.
    
    Args:
        kommune: Filter by specific kommune name (optional)
        is_highlighted: Filter by highlighted status (optional)
        category: Filter by category (optional)
        status: Filter by status (default: "Published")
        limit: Maximum number of articles to return (default: 20)
    
    Returns:
        Dictionary with list of newsletter articles
    """
    try:
        filters = {"status": status}
        
        if kommune:
            filters["kommune"] = kommune
        if is_highlighted is not None:
            if isinstance(is_highlighted, str):
                is_highlighted = is_highlighted.lower() == "true"
            filters["is_highlighted"] = 1 if is_highlighted else 0
        if category:
            filters["category"] = category
        
        newsletters = frappe.get_all(
            "Kommune Newsletter",
            filters=filters,
            fields=[
                "name", "kommune", "newsletter_date", "title", "summary",
                "category", "is_highlighted", "source_url", "tags"
            ],
            order_by="newsletter_date desc, is_highlighted desc",
            limit=limit
        )
        
        return {
            "success": True,
            "newsletters": newsletters,
            "count": len(newsletters),
            "filters_applied": filters,
            "message": f"Found {len(newsletters)} newsletter articles"
        }
    except Exception as e:
        frappe.log_error(f"Get kommune newsletters error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve kommune newsletters"
        }


@frappe.whitelist()
def get_highlighted_kommune_news(kommune: str = None, limit: int = 10) -> Dict[str, Any]:
    """
    Get highlighted kommune news articles.
    
    Args:
        kommune: Optional specific kommune name
        limit: Maximum number of articles to return (default: 10)
    
    Returns:
        Dictionary with list of highlighted news articles
    """
    try:
        filters = {
            "is_highlighted": 1,
            "status": "Published"
        }
        
        if kommune:
            filters["kommune"] = kommune
        
        newsletters = frappe.get_all(
            "Kommune Newsletter",
            filters=filters,
            fields=[
                "name", "kommune", "newsletter_date", "title", "summary",
                "category", "source_url", "tags", "full_content"
            ],
            order_by="newsletter_date desc",
            limit=limit
        )
        
        return {
            "success": True,
            "newsletters": newsletters,
            "count": len(newsletters),
            "kommune": kommune or "All",
            "message": f"Found {len(newsletters)} highlighted news articles"
        }
    except Exception as e:
        frappe.log_error(f"Get highlighted news error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve highlighted news"
        }
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
def get_marketplace_hustle_status() -> Dict[str, Any]:
    """
    Get the current status of the marketplace hustle routine.
    
    Returns:
        Dictionary with status information including active searches and recent activity
    """
    try:
        from assist.utils.marketplace_hustle import get_hustle_routine_status
        
        result = get_hustle_routine_status()
        return result
    except Exception as e:
        frappe.log_error(f"Get marketplace hustle status error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get marketplace hustle routine status"
        }


# ============================================================================
# Farm Season Calendar API Endpoints
# ============================================================================


@frappe.whitelist()
def get_planting_calendar(norwegian_zone: str = None, month: str = None) -> Dict[str, Any]:
    """
    Get planting calendar recommendations for Norwegian climate zones.
    
    Args:
        norwegian_zone: Norwegian climate zone (1-8, or "All Zones")
        month: Optional month to filter crops (e.g., "May")
    
    Returns:
        Dictionary with list of crops suitable for planting
    """
    try:
        filters = {}
        
        if norwegian_zone and norwegian_zone != "All Zones":
            filters["norwegian_zone"] = ["in", [norwegian_zone, "All Zones"]]
        
        if month:
            # Get crops where planting period includes this month
            filters["planting_start_month"] = ["<=", month]
            filters["planting_end_month"] = [">=", month]
        
        crops = frappe.get_all(
            "Crop",
            filters=filters,
            fields=[
                "name", "crop_name", "crop_family", "crop_type", "norwegian_zone",
                "planting_start_month", "planting_end_month", "harvest_start_month",
                "harvest_end_month", "days_to_maturity", "succession_planting_interval_days",
                "frost_tolerant", "sun_requirement", "water_requirement",
                "spacing_between_plants_cm", "spacing_between_rows_cm", "good_companions",
                "bad_companions"
            ],
            order_by="crop_name"
        )
        
        return {
            "success": True,
            "crops": crops,
            "count": len(crops),
            "zone": norwegian_zone or "All Zones",
            "month": month or "All Months",
            "message": f"Found {len(crops)} crops for planting"
        }
    except Exception as e:
        frappe.log_error(f"Get planting calendar error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get planting calendar"
        }


@frappe.whitelist()
def get_companion_planting_suggestions(crop_name: str) -> Dict[str, Any]:
    """
    Get companion planting suggestions for a specific crop.
    
    Args:
        crop_name: Name of the crop to get companion suggestions for
    
    Returns:
        Dictionary with good and bad companion plants
    """
    try:
        crop = frappe.get_doc("Crop", crop_name)
        
        good_companions = []
        if crop.good_companions:
            companion_names = [c.strip() for c in crop.good_companions.split(',')]
            for companion_name in companion_names:
                # Try to find the crop
                crops = frappe.get_all(
                    "Crop",
                    filters={"crop_name": ["like", f"%{companion_name}%"]},
                    fields=["crop_name", "crop_family", "crop_type"],
                    limit=1
                )
                if crops:
                    good_companions.append(crops[0])
                else:
                    good_companions.append({"crop_name": companion_name, "crop_family": "", "crop_type": ""})
        
        bad_companions = []
        if crop.bad_companions:
            companion_names = [c.strip() for c in crop.bad_companions.split(',')]
            for companion_name in companion_names:
                crops = frappe.get_all(
                    "Crop",
                    filters={"crop_name": ["like", f"%{companion_name}%"]},
                    fields=["crop_name", "crop_family", "crop_type"],
                    limit=1
                )
                if crops:
                    bad_companions.append(crops[0])
                else:
                    bad_companions.append({"crop_name": companion_name, "crop_family": "", "crop_type": ""})
        
        return {
            "success": True,
            "crop": crop_name,
            "good_companions": good_companions,
            "bad_companions": bad_companions,
            "message": f"Found {len(good_companions)} good and {len(bad_companions)} bad companions"
        }
    except Exception as e:
        frappe.log_error(f"Get companion planting suggestions error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get companion planting suggestions"
        }


@frappe.whitelist()
def get_crop_rotation_suggestions(garden_plot: str, previous_crop: str = None) -> Dict[str, Any]:
    """
    Get crop rotation suggestions based on previous crops in a garden plot.
    
    Args:
        garden_plot: Name of the garden plot
        previous_crop: Optional name of the crop previously planted
    
    Returns:
        Dictionary with suggested crops for rotation
    """
    try:
        suggestions = []
        avoid_crops = []
        
        if previous_crop:
            prev_crop_doc = frappe.get_doc("Crop", previous_crop)
            prev_family = prev_crop_doc.crop_family
            
            # Get crops from different families for rotation
            suggestions = frappe.get_all(
                "Crop",
                filters={
                    "crop_family": ["!=", prev_family]
                },
                fields=[
                    "crop_name", "crop_family", "crop_type", "planting_start_month",
                    "planting_end_month", "days_to_maturity"
                ],
                order_by="crop_name",
                limit=20
            )
            
            # Get crops from same family to avoid
            avoid_crops = frappe.get_all(
                "Crop",
                filters={
                    "crop_family": prev_family,
                    "crop_name": ["!=", previous_crop]
                },
                fields=["crop_name", "crop_family"],
                order_by="crop_name"
            )
        else:
            # No previous crop, suggest all crops
            suggestions = frappe.get_all(
                "Crop",
                fields=[
                    "crop_name", "crop_family", "crop_type", "planting_start_month",
                    "planting_end_month", "days_to_maturity"
                ],
                order_by="crop_name",
                limit=20
            )
        
        return {
            "success": True,
            "garden_plot": garden_plot,
            "previous_crop": previous_crop or "None",
            "suggested_crops": suggestions,
            "avoid_crops": avoid_crops,
            "rotation_tip": "Rotate crops from different families to prevent soil-borne diseases and pest buildup.",
            "message": f"Found {len(suggestions)} suggested crops for rotation"
        }
    except Exception as e:
        frappe.log_error(f"Get crop rotation suggestions error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get crop rotation suggestions"
        }


@frappe.whitelist()
def calculate_succession_planting(crop_name: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Calculate succession planting schedule for continuous harvest.
    
    Args:
        crop_name: Name of the crop
        start_date: Start date for planting (YYYY-MM-DD)
        end_date: End date for planting (YYYY-MM-DD)
    
    Returns:
        Dictionary with succession planting schedule
    """
    try:
        from datetime import datetime, timedelta
        from frappe.utils import getdate, add_days
        
        crop = frappe.get_doc("Crop", crop_name)
        
        if not crop.succession_planting_interval_days or crop.succession_planting_interval_days == 0:
            return {
                "success": False,
                "message": f"{crop_name} is not suitable for succession planting"
            }
        
        start = getdate(start_date)
        end = getdate(end_date)
        
        schedule = []
        current_date = start
        planting_number = 1
        
        while current_date <= end:
            harvest_date = add_days(current_date, crop.days_to_maturity) if crop.days_to_maturity else None
            
            schedule.append({
                "planting_number": planting_number,
                "planting_date": str(current_date),
                "expected_harvest_date": str(harvest_date) if harvest_date else "Unknown",
                "days_to_maturity": crop.days_to_maturity or 0
            })
            
            current_date = add_days(current_date, crop.succession_planting_interval_days)
            planting_number += 1
        
        return {
            "success": True,
            "crop": crop_name,
            "succession_interval_days": crop.succession_planting_interval_days,
            "planting_schedule": schedule,
            "total_plantings": len(schedule),
            "message": f"Created succession planting schedule with {len(schedule)} plantings"
        }
    except Exception as e:
        frappe.log_error(f"Calculate succession planting error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to calculate succession planting schedule"
        }


@frappe.whitelist()
def generate_garden_shopping_list(schedule_name: str) -> Dict[str, Any]:
    """
    Generate a shopping list for a garden planting schedule.
    
    Args:
        schedule_name: Name of the Garden Planting Schedule
    
    Returns:
        Dictionary with shopping list items
    """
    try:
        schedule = frappe.get_doc("Garden Planting Schedule", schedule_name)
        
        shopping_list = {}
        
        for item in schedule.planting_items:
            crop_key = item.crop
            if item.variety:
                crop_key = f"{item.crop} ({item.variety})"
            
            if crop_key not in shopping_list:
                shopping_list[crop_key] = {
                    "crop": item.crop,
                    "variety": item.variety or "Standard",
                    "total_quantity": 0,
                    "planting_dates": []
                }
            
            shopping_list[crop_key]["total_quantity"] += item.quantity or 1
            shopping_list[crop_key]["planting_dates"].append(str(item.planting_date))
        
        shopping_items = list(shopping_list.values())
        
        return {
            "success": True,
            "schedule_name": schedule_name,
            "garden_plot": schedule.garden_plot,
            "year": schedule.year,
            "shopping_list": shopping_items,
            "total_crop_types": len(shopping_items),
            "message": f"Generated shopping list with {len(shopping_items)} items"
        }
    except Exception as e:
        frappe.log_error(f"Generate shopping list error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate shopping list"
        }


@frappe.whitelist()
def get_upcoming_garden_tasks(days_ahead: int = 14) -> Dict[str, Any]:
    """
    Get upcoming planting and harvest tasks.
    
    Args:
        days_ahead: Number of days to look ahead (default: 14)
    
    Returns:
        Dictionary with upcoming tasks
    """
    try:
        from frappe.utils import getdate, add_days
        
        today = getdate()
        future_date = add_days(today, days_ahead)
        
        # Get all active planting schedules
        schedules = frappe.get_all(
            "Garden Planting Schedule",
            fields=["name", "schedule_name", "garden_plot", "year"]
        )
        
        tasks = {
            "planting": [],
            "harvest": []
        }
        
        for schedule_info in schedules:
            schedule = frappe.get_doc("Garden Planting Schedule", schedule_info["name"])
            
            for item in schedule.planting_items:
                # Check planting tasks
                if item.planting_date and item.status == "Planned":
                    planting_date = getdate(item.planting_date)
                    if today <= planting_date <= future_date:
                        days_until = (planting_date - today).days
                        tasks["planting"].append({
                            "schedule": schedule.schedule_name,
                            "garden_plot": schedule.garden_plot,
                            "crop": item.crop,
                            "variety": item.variety,
                            "date": str(item.planting_date),
                            "days_until": days_until,
                            "quantity": item.quantity
                        })
                
                # Check harvest tasks
                if item.expected_harvest_date and item.status in ["Seeded/Planted", "Growing"]:
                    harvest_date = getdate(item.expected_harvest_date)
                    if today <= harvest_date <= future_date:
                        days_until = (harvest_date - today).days
                        tasks["harvest"].append({
                            "schedule": schedule.schedule_name,
                            "garden_plot": schedule.garden_plot,
                            "crop": item.crop,
                            "variety": item.variety,
                            "date": str(item.expected_harvest_date),
                            "days_until": days_until,
                            "quantity": item.quantity
                        })
        
        # Sort by date
        tasks["planting"].sort(key=lambda x: x["date"])
        tasks["harvest"].sort(key=lambda x: x["date"])
        
        return {
            "success": True,
            "days_ahead": days_ahead,
            "planting_tasks": tasks["planting"],
            "harvest_tasks": tasks["harvest"],
            "total_tasks": len(tasks["planting"]) + len(tasks["harvest"]),
            "message": f"Found {len(tasks['planting'])} planting and {len(tasks['harvest'])} harvest tasks"
        }
    except Exception as e:
        frappe.log_error(f"Get upcoming garden tasks error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get upcoming garden tasks"
        }
