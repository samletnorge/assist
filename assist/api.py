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
        }


@frappe.whitelist()
def get_kommune_support_programs(kommune: str = None, status: str = "Active") -> Dict[str, Any]:
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
        )
        
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
