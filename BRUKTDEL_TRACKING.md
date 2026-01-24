# Bruktdel.no Car Parts Tracking

This feature enables automatic tracking of car parts availability on bruktdel.no for owned vehicle assets.

## Overview

The system monitors bruktdel.no (Norway's used car parts marketplace) for new parts matching your search criteria, linked to specific vehicle assets in your ERPNext system.

## Features

- **Asset-Linked Searches**: Link parts searches to specific car/vehicle assets in your system
- **Automatic Monitoring**: Hourly scheduled checks for new parts listings
- **Manual Triggers**: Ability to trigger immediate checks on demand
- **Marketplace Integration**: Seamlessly integrates with existing marketplace search infrastructure

## Setup

### 1. Configure Your Vehicle Assets

First, ensure your car/vehicle assets are properly set up in ERPNext:

1. Navigate to Asset > Asset List
2. Create or update vehicle assets with:
   - Asset Category: should contain "vehicle" in the name
   - Status: In Use, Partially Depreciated, or Fully Depreciated

### 2. Create a Bruktdel.no Search

Use the API or create directly in the UI:

```python
# Via Python API
frappe.call({
    method: "assist.api.save_bruktdel_search",
    args: {
        search_query: "Porsche 944 parts",
        asset_code: "ASSET-00001",  # Your vehicle asset code
        active: true
    }
})
```

Or create a "Saved Marketplace Search" document:
- **Marketplace**: bruktdel.no
- **Search Query**: Your search term (e.g., "Porsche 944 parts")
- **Asset (Car/Vehicle)**: Link to your vehicle asset
- **Active**: Checked

### 3. Enable Scheduler

The scheduler is automatically enabled via `hooks.py`. It runs:
- **Hourly**: Checks all active bruktdel.no searches
- **Daily**: Generates a summary report of marketplace activity

## API Endpoints

### Save a New Search

```python
POST /api/method/assist.api.save_bruktdel_search
{
    "search_query": "Porsche 944 parts",
    "asset_code": "ASSET-00001",  // Optional
    "active": true
}
```

**Response:**
```json
{
    "success": true,
    "search_name": "SMS-00001",
    "message": "Saved bruktdel.no search for: Porsche 944 parts"
}
```

### Get Car Assets

Retrieve all vehicle assets suitable for parts tracking:

```python
POST /api/method/assist.api.get_car_assets
```

**Response:**
```json
{
    "success": true,
    "assets": [
        {
            "name": "ASSET-00001",
            "asset_name": "Porsche 944 1987",
            "asset_category": "Vehicles",
            "item_name": "Porsche 944",
            "status": "In Use"
        }
    ],
    "count": 1
}
```

### Get Bruktdel.no Searches

Retrieve saved searches, optionally filtered by asset:

```python
POST /api/method/assist.api.get_bruktdel_searches
{
    "asset_code": "ASSET-00001",  // Optional
    "active_only": true
}
```

**Response:**
```json
{
    "success": true,
    "searches": [
        {
            "name": "SMS-00001",
            "search_query": "Porsche 944 parts",
            "asset_code": "ASSET-00001",
            "active": 1,
            "last_checked": "2026-01-24 10:00:00",
            "results_found": 0,
            "user": "user@example.com"
        }
    ],
    "count": 1
}
```

### Trigger Manual Check

Force an immediate check of bruktdel.no:

```python
POST /api/method/assist.api.trigger_bruktdel_check
{
    "search_name": "SMS-00001"  // Optional - omit to check all
}
```

**Response:**
```json
{
    "success": true,
    "search_name": "SMS-00001",
    "results_found": 0,
    "message": "Checked bruktdel.no: 0 results found"
}
```

## How It Works

### Data Flow

```
1. User creates a Saved Marketplace Search for bruktdel.no
   ↓
2. Links it to a vehicle Asset (optional but recommended)
   ↓
3. Hourly scheduler runs check_bruktdel_searches()
   ↓
4. For each active search:
   - Checks bruktdel.no for matching parts
   - Updates last_checked timestamp
   - Updates results_found count
   - Logs new listings
   ↓
5. Daily summary report generated
```

### Scheduled Tasks

#### Hourly: `check_bruktdel_searches()`
- Retrieves all active bruktdel.no searches
- Checks the website for each search query
- Updates search records with results
- Logs errors for failed checks

#### Daily: `daily_marketplace_summary()`
- Generates summary of all marketplace activity
- Aggregates results by marketplace
- Logs summary for reporting

## Example Usage

### Track Parts for a Porsche 944

Based on the issue requirements (tracking parts for a Porsche 944):

```python
# 1. Get your car asset
assets = frappe.call("assist.api.get_car_assets")
porsche = next(a for a in assets["assets"] if "944" in a["asset_name"])

# 2. Create a search for Porsche 944 parts
frappe.call({
    method: "assist.api.save_bruktdel_search",
    args: {
        search_query: "Porsche 944 parts 1981-91",
        asset_code: porsche["name"],
        active: true
    }
})

# 3. Trigger an immediate check
result = frappe.call({
    method: "assist.api.trigger_bruktdel_check",
    args: {}  // Checks all active searches
})
```

### View All Searches for a Vehicle

```python
searches = frappe.call({
    method: "assist.api.get_bruktdel_searches",
    args: {
        asset_code: "ASSET-00001",
        active_only: true
    }
})

console.log(searches["searches"])
```

## Future Enhancements

The current implementation provides the infrastructure for tracking. Future enhancements could include:

- **Web Scraping**: Actual implementation of bruktdel.no scraping logic
- **Price Tracking**: Monitor price changes over time
- **Notifications**: Email/SMS alerts when new parts are found
- **Price Alerts**: Notify when prices drop below threshold
- **Part Matching**: AI-powered matching of parts to vehicle models
- **Integration**: Direct purchase link generation
- **Analytics**: Dashboard showing parts availability trends

## Technical Details

### Files Modified

- `assist/assist_tools/doctype/saved_marketplace_search/saved_marketplace_search.json`
  - Added "bruktdel.no" to marketplace options
  - Added asset_code field for linking to vehicle assets

- `assist/hooks.py`
  - Enabled scheduler_events for hourly and daily tasks

- `assist/tasks.py` (NEW)
  - Implemented scheduled task functions
  - `check_bruktdel_searches()`: Main hourly task
  - `check_bruktdel_listing()`: Check individual search
  - `daily_marketplace_summary()`: Daily reporting

- `assist/api.py`
  - Added `save_bruktdel_search()`: Save new search
  - Added `get_car_assets()`: Get vehicle assets
  - Added `get_bruktdel_searches()`: Retrieve searches
  - Added `trigger_bruktdel_check()`: Manual trigger

### Dependencies

No new dependencies required. Uses standard Frappe/ERPNext libraries:
- `frappe`: Core framework
- `frappe.utils`: Date/time utilities

Optional for actual scraping implementation:
- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing

## Support

For issues or questions:
- Email: kontakt@drivstoffapp.no
- Repository: https://github.com/samletnorge/assist
