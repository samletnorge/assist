# Copyright (c) 2026, samletnorge and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from urllib.parse import urlencode


class MarketplaceListing(Document):
    def validate(self):
        """Validate the marketplace listing before saving."""
        if not self.currency:
            self.currency = frappe.defaults.get_global_default("currency") or "NOK"
        
        # Validate that either item_code or asset_code is provided based on listing_type
        if self.listing_type == "Sale" and not self.item_code:
            frappe.throw("Item Code is required for Sale listings")
        
        if self.listing_type == "Rental" and not self.asset_code:
            frappe.throw("Asset Code is required for Rental listings")
        
        if self.status == "Posted" and not self.posted_on:
            self.posted_on = frappe.utils.now()
        
        # Generate Google Maps route link if location information is available
        self._generate_gmaps_route_link()
    
    def _generate_gmaps_route_link(self):
        """Generate Google Maps route link based on pickup location."""
        if not self.pickup_location and not self.pickup_address:
            # No location information available
            self.gmaps_route_link = None
            return
        
        # Build the destination string
        destination_parts = []
        if self.pickup_address:
            destination_parts.append(self.pickup_address)
        if self.pickup_city:
            destination_parts.append(self.pickup_city)
        if self.pickup_postal_code:
            destination_parts.append(self.pickup_postal_code)
        
        # If we have structured address info, use it; otherwise use pickup_location
        if destination_parts:
            destination = ", ".join(destination_parts)
        else:
            destination = self.pickup_location
        
        # Generate Google Maps directions URL
        # Format: https://www.google.com/maps/dir/?api=1&destination=<address>
        params = {
            'api': '1',
            'destination': destination
        }
        
        self.gmaps_route_link = f"https://www.google.com/maps/dir/?{urlencode(params)}"
    
    def before_submit(self):
        """Actions before submitting the listing."""
        self.status = "Posted"
        if not self.posted_on:
            self.posted_on = frappe.utils.now()


@frappe.whitelist()
def generate_route_for_multiple_listings(listing_ids, start_location=None):
    """
    Generate a Google Maps route link for multiple marketplace listings.
    
    Args:
        listing_ids: List of Marketplace Listing IDs
        start_location: Optional starting location
    
    Returns:
        Dictionary with route link and listing details
    """
    import json
    
    if isinstance(listing_ids, str):
        listing_ids = json.loads(listing_ids)
    
    if not listing_ids:
        return {
            "success": False,
            "error": "No listings provided",
            "message": "At least one listing is required"
        }
    
    waypoints = []
    listings_info = []
    
    for listing_id in listing_ids:
        try:
            listing = frappe.get_doc("Marketplace Listing", listing_id)
            
            # Build destination string
            destination_parts = []
            if listing.pickup_address:
                destination_parts.append(listing.pickup_address)
            if listing.pickup_city:
                destination_parts.append(listing.pickup_city)
            if listing.pickup_postal_code:
                destination_parts.append(listing.pickup_postal_code)
            
            if destination_parts:
                destination = ", ".join(destination_parts)
            elif listing.pickup_location:
                destination = listing.pickup_location
            else:
                continue  # Skip listings without location
            
            waypoints.append(destination)
            listings_info.append({
                "name": listing.name,
                "title": listing.title,
                "location": destination,
                "seller_contact": listing.seller_contact,
                "seller_phone": listing.seller_phone
            })
        except Exception as e:
            frappe.log_error(f"Error processing listing {listing_id}: {str(e)}")
            continue
    
    if not waypoints:
        return {
            "success": False,
            "error": "No valid locations found",
            "message": "None of the listings have location information"
        }
    
    # Build Google Maps URL with multiple destinations
    # For multiple stops, use waypoints parameter
    params = {'api': '1'}
    
    if start_location:
        params['origin'] = start_location
    
    if len(waypoints) == 1:
        params['destination'] = waypoints[0]
    else:
        # Last waypoint is destination, rest are waypoints
        params['destination'] = waypoints[-1]
        if len(waypoints) > 1:
            params['waypoints'] = '|'.join(waypoints[:-1])
    
    route_link = f"https://www.google.com/maps/dir/?{urlencode(params)}"
    
    return {
        "success": True,
        "route_link": route_link,
        "listings": listings_info,
        "total_stops": len(waypoints),
        "message": f"Route generated for {len(waypoints)} pickup locations"
    }
