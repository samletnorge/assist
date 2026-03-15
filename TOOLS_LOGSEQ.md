- # Assist MCP Tools — Logseq Reference
  - type:: [[MCP Tools Reference]]
  - tags:: [[Assist]] [[ERPNext]] [[MCP]] [[Tools]]
  - description:: All 24 MCP tools exposed by the Assist ERPNext app, formatted for rebuilding in Logseq.

- ## Marketplace & Listings

  - ### `post_to_marketplace`
    - **Description**: Post stock items or assets to marketplaces like Facebook Marketplace, FINN.no, leid.no, or other rental services.
    - **Parameters**:
      - `marketplace` — Target marketplace (`'Facebook Marketplace'`, `'FINN.no'`, `'leid.no'`, `'Other Rental Service'`, `'Other'`)
      - `title` — Listing title
      - `description` — Listing description
      - `price` — Listing price (sale price or rental rate)
      - `item_code` — The ERPNext item code to post (for Sale listings)
      - `asset_code` — The ERPNext asset code to post (for Rental listings)
      - `listing_type` — Type of listing (`'Sale'` or `'Rental'`)
      - `images` — List of image URLs or paths
    - **Returns**: Dictionary with posting status and listing ID

  - ### `track_saved_search`
    - **Description**: Track and save search queries based on purchase or material request items.
    - **Parameters**:
      - `user` — ERPNext user ID
      - `search_query` — The search query to track
      - `marketplace` — Target marketplace for the search
      - `search_type` — Type of search (`'purchase_request'` or `'material_request'`)
    - **Returns**: Dictionary with search tracking status

  - ### `get_rental_eligible_assets`
    - **Description**: Get list of company-owned assets that are eligible for rental posting to leid.no and other rental services. Assets are identified by their chart of account codes (e.g., 1202 - Maskiner og anlegg, 1203 - Inventar, 1204 - Transportmidler).
    - **Parameters**:
      - `company` — Company name (optional, defaults to default company)
      - `asset_category` — Filter by asset category (optional)
      - `chart_of_account_code` — Filter by chart of account code like `'1202'`, `'1203'`, `'1204'` (optional)
    - **Returns**: Dictionary with list of rental-eligible assets

  - ### `post_asset_for_rental`
    - **Description**: Post company-owned assets (tools, equipment) to rental services like leid.no. This is a convenience wrapper around `post_to_marketplace` specifically for rental listings.
    - **Parameters**:
      - `asset_code` — The ERPNext asset code to post for rental
      - `marketplace` — Target rental service (`'leid.no'`, `'Other Rental Service'`, etc.)
      - `title` — Listing title
      - `description` — Listing description
      - `rental_rate` — Rental rate per period (day/week/month)
      - `images` — List of image URLs or paths
    - **Returns**: Dictionary with posting status and listing ID

  - ### `manage_marketplace_listings_with_phone_ctrl`
    - **Description**: Manage marketplace listings (Facebook, FINN.no) using phone control. Retrieves Material Request items saved by user and communicates with sellers using standard messages.
    - **Parameters**:
      - `material_request_items` — List of Material Request item IDs to search for
      - `marketplace` — Target marketplace (`'facebook'` or `'finn'`)
      - `action` — Action to perform (`'search'`, `'message_seller'`, `'add_to_list'`)
      - `message_template` — Template to use (`'standard'`, `'storage'`, `'free_goods'`, `'apology'`)
    - **Returns**: Dictionary with marketplace action results and communication status

  - ### `orchestrate_pickup_route`
    - **Description**: Orchestrate efficient pickup routes for marketplace listings by contacting sellers. Schedules pickups and optimizes route for a specific day with standard Norwegian messages. Generates Google Maps route link with all pickup locations.
    - **Parameters**:
      - `listings` — List of marketplace listing IDs to schedule pickups for
      - `start_location` — Starting location for the route
      - `preferred_date` — Preferred pickup date (YYYY-MM-DD format)
      - `message_type` — Type of message (`'standard'`, `'storage'`, `'free_goods'`, `'apology'`)
    - **Returns**: Dictionary with route plan, Google Maps link, suggested messages, and seller contact status

  - ### `run_marketplace_hustle_routine`
    - **Description**: Trigger the marketplace hustle routine to check saved marketplace searches. Checks all active saved marketplace searches (finn.no, Facebook Marketplace) for new items matching building materials, pallets, tracks, or other needed items. When new items are found, checks if they match Material Requests or Tasks, and creates notifications for matches.
    - **Parameters**: _(none)_
    - **Returns**: Dictionary with processing results including searches processed, items found, and matches created

  - ### `find_warehouses_on_finn`
    - **Description**: Find warehouses anywhere in Norway (including northern regions) by searching FINN.no. Can use phone control to automate search and add results to ERPNext.
    - **Parameters**:
      - `location` — Location to search for warehouses (e.g., `'Tromsø'`, `'Bodø'`, `'Lyngdal'`)
      - `search_query` — Search query for warehouses (default: `'lager'`)
      - `region` — Optional region filter (e.g., `'Nord-Norge'`, `'Troms'`)
      - `add_to_erpnext` — If `True`, automatically adds found warehouses to ERPNext
      - `phone_control` — If `True`, uses phone control for automated browsing
    - **Returns**: Dictionary with found warehouses and ERPNext creation status

- ## Inventory & Stock

  - ### `quick_add_item_from_camera`
    - **Description**: Quickly add a new item (stock or asset) using camera capture with automatic background removal. Useful for warehouses with disorganized or new items.
    - **Parameters**:
      - `image_data` — Base64 encoded image data or file path
      - `warehouse` — Target warehouse for the item
      - `item_group` — Optional item group classification
      - `valuation_rate` — Optional valuation rate for the item
      - `remove_background` — Automatically remove background from image (default: `True`)
      - `enhance_image` — Automatically enhance image quality (default: `True`)
    - **Returns**: Dictionary with item creation status and item code

  - ### `scan_barcode_for_location`
    - **Description**: Scan a barcode to quickly check which warehouse an item should be in.
    - **Parameters**:
      - `barcode` — The barcode value to scan
    - **Returns**: Dictionary with warehouse location information

  - ### `get_item_details`
    - **Description**: Get detailed information about an item including stock levels across warehouses.
    - **Parameters**:
      - `item_code` — The ERPNext item code
    - **Returns**: Dictionary with comprehensive item details

  - ### `scan_receipt_and_add_items`
    - **Description**: Scan a receipt image using OCR and automatically add items as stock or assets.
    - **Parameters**:
      - `receipt_image` — Base64 encoded receipt image
      - `add_as` — Type to add items as (`'stock'` or `'asset'`)
      - `warehouse` — Target warehouse for stock items
      - `cost_center` — Cost center for asset items
    - **Returns**: Dictionary with scanned items and creation status

  - ### `batch_camera_upload_items`
    - **Description**: Add multiple items to stock using phone camera in batch mode. Very intuitive for quickly photographing and adding many items at once. Automatically processes images with background removal and enhancement.
    - **Parameters**:
      - `images` — List of base64 encoded image strings from phone camera
      - `warehouse` — Target warehouse for all items
      - `upload_name` — Optional descriptive name for this batch upload
      - `item_group` — Optional item group classification for all items
      - `valuation_rate` — Optional default valuation rate for all items
      - `remove_background` — Automatically remove background from all images (default: `True`)
      - `enhance_image` — Automatically enhance image quality (default: `True`)
    - **Returns**: Dictionary with batch upload results including items created and any failures

  - ### `compare_vendor_prices`
    - **Description**: Compare vendor prices for an item using Prisjakt.no and internal vendor catalog. Suggests cheapest vendor and pulls vendor catalog.
    - **Parameters**:
      - `item_name` — Name or description of item to search
      - `search_prisjakt` — Whether to search Prisjakt.no (default: `True`)
    - **Returns**: Dictionary with vendor comparisons and catalog suggestions

  - ### `query_inventory_natural_language`
    - **Description**: Answer natural language queries about inventory. Examples: `"do we have pliers?"`, `"where is the hammer?"`, `"how many screws do we have?"`
    - **Parameters**:
      - `query` — Natural language question about inventory
    - **Returns**: Dictionary with query results in natural language

- ## Norwegian Business & Government

  - ### `import_norwegian_chart_of_accounts`
    - **Description**: Import Norwegian chart of accounts following NS 4102 standard (private sector) or DFØ standard (government sector).
    - **Parameters**:
      - `standard` — `"NS4102"` for private sector or `"DFO"` for government sector (DFØ — Direktoratet for Forvaltning og Økonomi)
      - `company` — Company name to import accounts for (uses default if not provided)
    - **Returns**: Dictionary with import results including number of accounts created

  - ### `manage_skatteetaten_submissions`
    - **Description**: Interact with Skatteetaten (Norwegian Tax Authority) for tax-related submissions. Supports employee registration (A-melding), tax reports, deductions, and deadline checking.
    - **Parameters**:
      - `action` — Type of interaction: `'employee_registration'`, `'tax_report'`, `'deduction_request'`, `'check_deadlines'`, `'check_account'`
      - `data` — Additional data for the submission (e.g., employee info, tax amounts)
    - **Returns**: Dictionary with submission status and instructions for phone control if API unavailable

  - ### `submit_lyngdal_kommune_application`
    - **Description**: Submit applications to Norwegian municipal services (kommune). Supports building permits, renovation permits, and property upgrades.
    - **Parameters**:
      - `kommune` — Municipality name (e.g., `"Lyngdal"`, `"Oslo"`, `"Bergen"`)
      - `application_type` — Type of application: `'building_permit'`, `'renovation_permit'`, `'property_upgrade'`
      - `data` — Application data (property address, work description, estimated cost, etc.)
    - **Returns**: Dictionary with submission status and tracking information

  - ### `get_support_programs`
    - **Description**: Get list of Norwegian support programs, grants, and deductions (støtte og fradrag). Search and retrieve information about available financial support programs in Norway for different entities including private persons, companies, housing projects, and farms.
    - **Parameters**:
      - `entity_type` — Filter by eligible entity type (e.g., `'private_person'`, `'company'`, `'housing'`, `'farm'`)
      - `provider` — Filter by provider organization (e.g., `'Enova'`, `'Husbanken'`, `'Innovasjon Norge'`)
      - `program_type` — Filter by program type (e.g., `'grant'`, `'loan'`, `'deduction'`)
      - `category` — Filter by category (e.g., `'Energi'`, `'Bolig'`, `'Landbruk'`)
    - **Returns**: Dictionary with list of matching support programs

  - ### `get_enova_support_programs`
    - **Description**: Get all active Enova support programs (Enova støtte). Retrieves comprehensive information about Enova's support programs for energy efficiency improvements (varmepumper, isolasjon), renewable energy installations (solceller, varmeanlegg), business energy optimization, and sustainable transportation. Enova is the Norwegian government enterprise responsible for promoting environmentally friendly production and consumption of energy.
    - **Parameters**: _(none)_
    - **Returns**: Dictionary with detailed information about all active Enova programs

  - ### `search_norwegian_support`
    - **Description**: Search Norwegian support programs by keyword. Searches across program names, descriptions, and categories to find relevant support programs, grants, and deductions.
    - **Parameters**:
      - `search_term` — Keyword or phrase to search for (in Norwegian or English), e.g., `"varmepumpe"`, `"solar"`, `"byggesøknad"`, `"BSU"`
    - **Returns**: Dictionary with list of matching support programs

- ## Technical Standards & Documentation

  - ### `generate_rds_81346_designation`
    - **Description**: Generate ISO/IEC 81346 (RDS) reference designations for equipment and systems. Creates standardized identifiers for industrial systems, installations, and equipment.
    - **Parameters**:
      - `equipment_name` — Name of the equipment/component
      - `function_aspect` — Functional classification (what it does) — prefix with `'='`
      - `product_aspect` — Product classification (what it is) — prefix with `'-'`
      - `location_aspect` — Location classification (where it is) — prefix with `'+'`
      - `parent_system` — Parent system reference designation
    - **Returns**: Dictionary with generated RDS designation and metadata

  - ### `create_s1000d_data_module`
    - **Description**: Create S1000D Issue 6 compliant data modules for technical publications. Generates standardized XML-based technical documentation for aerospace/defense equipment.
    - **Parameters**:
      - `item_code` — ERPNext item code for the equipment
      - `data_module_code` — S1000D Data Module Code (DMC)
      - `title` — Data module title
      - `content_type` — Type of content (`'procedural'`, `'descriptive'`, `'fault'`, `'crew'`)
      - `issue_number` — S1000D issue number (default: `'6'`)
    - **Returns**: Dictionary with data module structure and metadata

- ## DevOps & GitHub

  - ### `import_github_repos_as_assets`
    - **Description**: Import all GitHub repositories as assets in ERPNext. Fetches repos from a user or organization and creates asset records.
    - **Parameters**:
      - `username` — GitHub username to import repos from
      - `organization` — GitHub organization name to import repos from
      - `github_token` — GitHub personal access token (optional, for private repos)
      - `import_as_assets` — If `True`, creates assets; if `False`, creates items only
      - `asset_category` — Asset category to assign (e.g., `'Software'`, `'Code Repository'`)
    - **Returns**: Dictionary with imported repos and asset creation status
