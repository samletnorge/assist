"""
Scheduled tasks for Assist Tools

This module contains scheduled tasks that run at various intervals to
track marketplace searches, update prices, and check for new listings.
"""

import frappe
from frappe import _
from frappe.utils import now_datetime, add_days, get_datetime

# TODO: Uncomment when implementing actual web scraping
# import requests
# from bs4 import BeautifulSoup


def check_bruktdel_searches():
    """
    Check active bruktdel.no searches for new parts listings.
    
    This function runs hourly and:
    1. Gets all active Saved Marketplace Search records for bruktdel.no
    2. Checks bruktdel.no for new listings matching the search criteria
    3. Updates the last_checked timestamp and results_found count
    4. Logs any new or updated listings
    """
    try:
        # Get all active bruktdel.no searches
        searches = frappe.get_all(
            "Saved Marketplace Search",
            filters={
                "marketplace": "bruktdel.no",
                "active": 1
            },
            fields=["name", "search_query", "asset_code", "last_checked", "user"]
        )
        
        if not searches:
            frappe.logger().info("No active bruktdel.no searches found")
            return
        
        frappe.logger().info(f"Checking {len(searches)} bruktdel.no searches")
        
        for search in searches:
            try:
                # Check bruktdel.no for this search
                results_count = check_bruktdel_listing(
                    search_query=search.get("search_query"),
                    asset_code=search.get("asset_code"),
                    user=search.get("user")
                )
                
                # Update the search record
                doc = frappe.get_doc("Saved Marketplace Search", search.get("name"))
                doc.last_checked = now_datetime()
                doc.results_found = results_count
                doc.save(ignore_permissions=True)
                frappe.db.commit()
                
                frappe.logger().info(
                    f"Updated search {search.get('name')}: {results_count} results found"
                )
                
            except Exception as e:
                frappe.log_error(
                    message=str(e),
                    title=f"Error checking bruktdel.no search {search.get('name')}"
                )
                
    except Exception as e:
        frappe.log_error(
            message=str(e),
            title="Error in check_bruktdel_searches scheduled task"
        )


def check_bruktdel_listing(search_query, asset_code=None, user=None):
    """
    Check bruktdel.no for listings matching the search query.
    
    Args:
        search_query: The search term to look for
        asset_code: Optional asset code to associate findings with
        user: User who created the search
        
    Returns:
        int: Number of results found
    """
    try:
        # The bruktdel.no URL pattern based on the issue
        # Example: https://www.bruktdel.no/nbf/Bildeler/porsche/944-1981-91#velgHvor
        
        # For now, we'll log that we would check the site
        # In a production system, you would:
        # 1. Build the proper URL based on search_query and asset_code
        # 2. Make HTTP request to bruktdel.no
        # 3. Parse the HTML response
        # 4. Extract part listings
        # 5. Store or notify about new parts
        
        frappe.logger().info(
            f"Checking bruktdel.no for query: {search_query}, asset: {asset_code}"
        )
        
        # Placeholder: Return 0 until actual scraping is implemented
        # In production, you would return the actual count of listings found
        return 0
        
    except Exception as e:
        frappe.log_error(
            message=str(e),
            title=f"Error checking bruktdel.no for query: {search_query}"
        )
        return 0


def daily_marketplace_summary():
    """
    Generate a daily summary of marketplace search activity.
    
    This function runs daily and creates a summary report of:
    - New listings found across all marketplaces
    - Price changes
    - Popular searches
    """
    try:
        # Get all active searches checked in the last 24 hours
        yesterday = add_days(now_datetime(), -1)
        
        searches = frappe.get_all(
            "Saved Marketplace Search",
            filters={
                "active": 1,
                "last_checked": [">=", yesterday]
            },
            fields=["marketplace", "results_found", "search_query"]
        )
        
        if not searches:
            return
        
        # Group by marketplace
        summary = {}
        for search in searches:
            marketplace = search.get("marketplace")
            if marketplace not in summary:
                summary[marketplace] = {
                    "total_searches": 0,
                    "total_results": 0,
                    "queries": []
                }
            
            summary[marketplace]["total_searches"] += 1
            summary[marketplace]["total_results"] += search.get("results_found", 0)
            summary[marketplace]["queries"].append(search.get("search_query"))
        
        # Log the summary
        frappe.logger().info(f"Daily marketplace summary: {summary}")
        
    except Exception as e:
        frappe.log_error(
            message=str(e),
            title="Error in daily_marketplace_summary scheduled task"
        )


def send_garden_reminders():
    """
    Send email reminders for upcoming planting and harvest tasks.
    
    This function runs daily and:
    1. Gets all active Garden Planting Schedules with email reminders enabled
    2. Checks for upcoming planting and harvest dates
    3. Sends email reminders to users
    """
    try:
        from frappe.utils import getdate, add_days
        from datetime import datetime
        
        today = getdate()
        
        # Get all schedules with reminders enabled
        schedules = frappe.get_all(
            "Garden Planting Schedule",
            filters={
                "enable_email_reminders": 1
            },
            fields=["name", "schedule_name", "garden_plot", "reminder_email",
                   "reminder_days_before_planting", "reminder_days_before_harvest"]
        )
        
        if not schedules:
            frappe.logger().info("No garden planting schedules with reminders enabled")
            return
        
        frappe.logger().info(f"Checking {len(schedules)} garden planting schedules for reminders")
        
        for schedule_info in schedules:
            try:
                schedule = frappe.get_doc("Garden Planting Schedule", schedule_info["name"])
                
                if not schedule.reminder_email:
                    continue
                
                reminders = schedule.get_planting_reminders()
                
                if reminders:
                    # Send email with reminders
                    send_reminder_email(schedule, reminders)
                    
                    frappe.logger().info(
                        f"Sent {len(reminders)} reminders for schedule {schedule.name}"
                    )
            
            except Exception as e:
                frappe.log_error(
                    message=str(e),
                    title=f"Error processing reminders for schedule {schedule_info['name']}"
                )
        
    except Exception as e:
        frappe.log_error(
            message=str(e),
            title="Error in send_garden_reminders scheduled task"
        )


def send_reminder_email(schedule, reminders):
    """
    Send email reminder for garden tasks.
    
    Args:
        schedule: Garden Planting Schedule document
        reminders: List of reminder dictionaries
    """
    try:
        from frappe.utils import cstr
        
        # Build email content with proper HTML escaping
        planting_reminders = [r for r in reminders if r["type"] == "planting"]
        harvest_reminders = [r for r in reminders if r["type"] == "harvest"]
        
        # Escape HTML in user-provided data
        schedule_name = frappe.utils.html_escape(cstr(schedule.schedule_name))
        garden_plot = frappe.utils.html_escape(cstr(schedule.garden_plot))
        
        message = f"""
        <h2>Garden Planting Reminders for {schedule_name}</h2>
        <p>Garden Plot: {garden_plot}</p>
        """
        
        if planting_reminders:
            message += "<h3>Upcoming Planting Tasks</h3><ul>"
            for reminder in planting_reminders:
                crop = frappe.utils.html_escape(cstr(reminder['crop']))
                variety = frappe.utils.html_escape(cstr(reminder.get('variety', '')))
                variety_text = f" ({variety})" if variety else ""
                days_until = int(reminder['days_until'])
                date = cstr(reminder['date'])
                message += f"<li><strong>{crop}{variety_text}</strong> - Plant in {days_until} days ({date})</li>"
            message += "</ul>"
        
        if harvest_reminders:
            message += "<h3>Upcoming Harvest Tasks</h3><ul>"
            for reminder in harvest_reminders:
                crop = frappe.utils.html_escape(cstr(reminder['crop']))
                variety = frappe.utils.html_escape(cstr(reminder.get('variety', '')))
                variety_text = f" ({variety})" if variety else ""
                days_until = int(reminder['days_until'])
                date = cstr(reminder['date'])
                message += f"<li><strong>{crop}{variety_text}</strong> - Ready to harvest in {days_until} days ({date})</li>"
            message += "</ul>"
        
        message += """
        <p>Good luck with your gardening!</p>
        <p><small>This is an automated reminder from your Assist Farm Season Calendar.</small></p>
        """
        
        # Send email
        frappe.sendmail(
            recipients=[schedule.reminder_email],
            subject=f"Garden Reminders: {schedule.schedule_name}",
            message=message
        )
        
    except Exception as e:
        frappe.log_error(
            message=str(e),
            title=f"Error sending reminder email for schedule {schedule.name}"
        )
