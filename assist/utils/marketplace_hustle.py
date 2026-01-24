"""
Marketplace Hustle Routine

This module implements automatic monitoring of marketplace listings (finn.no, Facebook Marketplace)
and matches them with Material Requests and Tasks that might need those items.
"""

import frappe
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


def check_marketplace_searches() -> Dict[str, Any]:
    """
    Main hustle routine that checks all active saved marketplace searches
    and processes new items found.
    
    This function is meant to be called by a scheduled task.
    
    Returns:
        Dictionary with processing results
    """
    try:
        # Get all active saved marketplace searches
        searches = frappe.get_all(
            "Saved Marketplace Search",
            filters={"active": 1},
            fields=["name", "user", "search_query", "marketplace", "search_type", "last_checked"]
        )
        
        results = {
            "searches_processed": 0,
            "items_found": 0,
            "matches_created": 0,
            "errors": []
        }
        
        for search in searches:
            try:
                # Process each search
                search_result = process_single_search(search)
                results["searches_processed"] += 1
                results["items_found"] += search_result.get("items_found", 0)
                results["matches_created"] += search_result.get("matches_created", 0)
                
                # Update last_checked timestamp
                frappe.db.set_value(
                    "Saved Marketplace Search",
                    search["name"],
                    "last_checked",
                    frappe.utils.now()
                )
                frappe.db.set_value(
                    "Saved Marketplace Search",
                    search["name"],
                    "results_found",
                    search_result.get("items_found", 0)
                )
                
            except Exception as search_error:
                error_msg = f"Error processing search {search['name']}: {str(search_error)}"
                frappe.log_error(error_msg)
                results["errors"].append(error_msg)
        
        frappe.db.commit()
        
        return {
            "success": True,
            "results": results,
            "message": f"Processed {results['searches_processed']} searches, found {results['items_found']} items, created {results['matches_created']} matches"
        }
        
    except Exception as e:
        frappe.log_error(f"Marketplace hustle routine error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to run marketplace hustle routine"
        }


def process_single_search(search: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single saved marketplace search.
    
    Args:
        search: Dictionary containing search details
    
    Returns:
        Dictionary with processing results
    """
    # Simulate fetching new items from marketplace
    # In a real implementation, this would call actual marketplace APIs
    new_items = fetch_marketplace_items(
        search["marketplace"],
        search["search_query"],
        search.get("last_checked")
    )
    
    matches_created = 0
    
    # Check if items match Material Requests or Tasks
    # Both 'material_request' and 'purchase_request' types should check Material Requests
    for item in new_items:
        if search.get("search_type") in ("material_request", "purchase_request"):
            # Check against Material Requests
            if match_with_material_requests(item, search["search_query"]):
                matches_created += 1
        else:
            # For other types or no type specified, check against Tasks
            if match_with_tasks(item, search["search_query"]):
                matches_created += 1
    
    return {
        "items_found": len(new_items),
        "matches_created": matches_created
    }


def fetch_marketplace_items(
    marketplace: str,
    search_query: str,
    last_checked: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch items from marketplace based on search query.
    
    This is a placeholder implementation. In production, this would:
    - Call finn.no API for FINN.no marketplace
    - Use Facebook Graph API for Facebook Marketplace
    - Parse RSS feeds or use web scraping as fallback
    
    Args:
        marketplace: Marketplace name ('Facebook Marketplace' or 'FINN.no')
        search_query: Search query string
        last_checked: Timestamp of last check (to fetch only new items)
    
    Returns:
        List of items found
    """
    # Placeholder implementation
    # In production, this would call actual marketplace APIs
    items = []
    
    # Log the search attempt
    frappe.logger().info(
        f"Fetching items from {marketplace} for query: {search_query}"
    )
    
    # Return empty list for now - actual implementation would fetch from APIs
    return items


def match_with_material_requests(item: Dict[str, Any], search_query: str) -> bool:
    """
    Check if a marketplace item matches any open Material Requests.
    
    Args:
        item: Dictionary containing item details from marketplace
        search_query: Original search query
    
    Returns:
        True if a match is found and notification created, False otherwise
    """
    try:
        # Get open Material Requests with items matching the search query
        # Using parameterized queries which provides SQL injection protection
        material_requests = frappe.db.sql("""
            SELECT 
                mr.name as material_request,
                mri.name as item_id,
                mri.item_code,
                mri.item_name,
                mri.qty,
                mri.description
            FROM 
                `tabMaterial Request` mr
            INNER JOIN 
                `tabMaterial Request Item` mri ON mr.name = mri.parent
            WHERE 
                mr.docstatus = 1
                AND mr.status IN ('Pending', 'Partially Ordered')
                AND (
                    mri.item_name LIKE %(search_pattern)s
                    OR mri.description LIKE %(search_pattern)s
                    OR mri.item_code LIKE %(search_pattern)s
                )
        """, {
            "search_pattern": f"%{search_query}%"
        }, as_dict=True)
        
        if material_requests:
            # Create notification or log for matching items
            for mr in material_requests:
                create_match_notification(
                    item=item,
                    reference_doctype="Material Request",
                    reference_name=mr["material_request"],
                    match_type="material_request"
                )
            return True
        
        return False
        
    except Exception as e:
        frappe.log_error(f"Error matching with Material Requests: {str(e)}")
        return False


def match_with_tasks(item: Dict[str, Any], search_query: str) -> bool:
    """
    Check if a marketplace item matches any open Tasks.
    
    Args:
        item: Dictionary containing item details from marketplace
        search_query: Original search query
    
    Returns:
        True if a match is found and notification created, False otherwise
    """
    try:
        # Get open Tasks with descriptions matching the search query
        # Using parameterized queries which provides SQL injection protection
        tasks = frappe.db.sql("""
            SELECT 
                name,
                subject,
                description,
                project
            FROM 
                `tabTask`
            WHERE 
                status IN ('Open', 'Working', 'Pending Review')
                AND (
                    subject LIKE %(search_pattern)s
                    OR description LIKE %(search_pattern)s
                )
        """, {
            "search_pattern": f"%{search_query}%"
        }, as_dict=True)
        
        if tasks:
            # Create notification or log for matching items
            for task in tasks:
                create_match_notification(
                    item=item,
                    reference_doctype="Task",
                    reference_name=task["name"],
                    match_type="task"
                )
            return True
        
        return False
        
    except Exception as e:
        frappe.log_error(f"Error matching with Tasks: {str(e)}")
        return False


def create_match_notification(
    item: Dict[str, Any],
    reference_doctype: str,
    reference_name: str,
    match_type: str
) -> None:
    """
    Create a notification when a marketplace item matches a Material Request or Task.
    
    Args:
        item: Dictionary containing item details from marketplace
        reference_doctype: Doctype of the matched document (Material Request or Task)
        reference_name: Name of the matched document
        match_type: Type of match ('material_request' or 'task')
    """
    try:
        # Get values from item and sanitize them to prevent XSS
        item_title = frappe.utils.escape_html(item.get("title", "Unknown Item"))
        item_price = frappe.utils.escape_html(str(item.get("price", "N/A")))
        item_url = item.get("url", "")
        marketplace = frappe.utils.escape_html(item.get("marketplace", "Unknown"))
        
        # Build comment text with sanitized values
        comment_text = f"""
<b>Marketplace Match Found!</b><br>
A matching item was found on {marketplace}:<br>
<br>
<b>Item:</b> {item_title}<br>
<b>Price:</b> {item_price}<br>
"""
        
        # Validate and sanitize URL before adding to HTML
        if item_url:
            # Basic URL validation - check if it starts with http:// or https://
            if item_url.startswith("http://") or item_url.startswith("https://"):
                # Escape URL for HTML context
                safe_url = frappe.utils.escape_html(item_url)
                comment_text += f'<b>URL:</b> <a href="{safe_url}" target="_blank">{safe_url}</a><br>'
            else:
                # Don't include potentially malicious URLs
                comment_text += f'<b>URL:</b> [Invalid URL format]<br>'
        
        comment_text += f"<br><i>Found by marketplace hustle routine at {frappe.utils.now()}</i>"
        
        # Add comment to the document
        frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Comment",
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
            "content": comment_text
        }).insert(ignore_permissions=True)
        
        # Also create a notification for the document owner
        doc = frappe.get_doc(reference_doctype, reference_name)
        if hasattr(doc, 'owner'):
            frappe.publish_realtime(
                event="marketplace_match_found",
                message={
                    "reference_doctype": reference_doctype,
                    "reference_name": reference_name,
                    "item": item,
                    "match_type": match_type
                },
                user=doc.owner
            )
        
    except Exception as e:
        frappe.log_error(f"Error creating match notification: {str(e)}")


def get_hustle_routine_status() -> Dict[str, Any]:
    """
    Get the current status of the marketplace hustle routine.
    
    Returns:
        Dictionary with status information
    """
    try:
        # Get statistics about saved searches
        total_searches = frappe.db.count("Saved Marketplace Search")
        active_searches = frappe.db.count("Saved Marketplace Search", {"active": 1})
        
        # Get recent activity
        recent_searches = frappe.get_all(
            "Saved Marketplace Search",
            filters={"active": 1},
            fields=["name", "search_query", "marketplace", "last_checked", "results_found"],
            order_by="last_checked desc",
            limit=10
        )
        
        return {
            "success": True,
            "status": {
                "total_searches": total_searches,
                "active_searches": active_searches,
                "recent_searches": recent_searches
            },
            "message": f"{active_searches} active searches out of {total_searches} total"
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting hustle routine status: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get hustle routine status"
        }
