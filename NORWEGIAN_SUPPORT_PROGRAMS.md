# Norwegian Support Programs Index

This document describes the Norwegian Support Programs Index feature, which provides a comprehensive database of available grants, deductions, and support programs in Norway.

## Overview

The Norwegian Support Programs Index (Støtte og Fradrag Index) is a comprehensive database that allows users to search and browse:

- **Støtte** (Grants and Support): Financial support from various Norwegian organizations
- **Fradrag** (Tax Deductions): Available tax deductions for individuals and businesses
- **Lån** (Loans): Government-backed loan programs
- **Tilskudd** (Subsidies): Various subsidy programs

### Supported Entity Types

The system categorizes support programs by eligible entities:

1. **Private Person** (Privatperson): Support available to individuals
2. **Company** (Bedrift): Support available to businesses
3. **Housing** (Bolig): Support for housing projects and home improvements
4. **Farm** (Gård): Support for agricultural operations

### Supported Providers

Programs from major Norwegian support organizations:

- **Enova**: Energy efficiency and renewable energy support
- **Kommune**: Municipal support programs and building permits
- **Skatteetaten**: Tax deductions (fradrag)
- **Husbanken**: Housing loans and grants
- **Innovasjon Norge**: Business innovation support
- **Norges Forskningsråd**: Research council funding
- **Landsbruksdirektoratet**: Agricultural support

---

## DocTypes

### 1. Norwegian Support Program

Main doctype for storing support program information.

**Key Fields:**
- `program_name`: Name of the support program
- `program_code`: Unique identifier (auto-generated)
- `provider`: Organization providing the support
- `program_type`: Type of support (Støtte, Fradrag, Lån, etc.)
- `category`: Category (Energi, Bygg, Landbruk, etc.)
- `status`: Active, Inactive, Upcoming, Expired

**Eligibility Fields:**
- `eligible_for_private_person`: Boolean
- `eligible_for_company`: Boolean
- `eligible_for_housing`: Boolean
- `eligible_for_farm`: Boolean
- `additional_eligibility_criteria`: Text description

**Financial Information:**
- `support_amount_min`: Minimum support amount
- `support_amount_max`: Maximum support amount
- `currency`: Currency (default: NOK)
- `percentage_coverage`: Percentage of costs covered
- `max_coverage_amount`: Maximum coverage limit

**Dates:**
- `application_deadline`: Application deadline
- `program_start_date`: Program start date
- `program_end_date`: Program end date
- `application_period`: Description of application period

**Child Tables:**
- `requirements`: List of program requirements (via Norwegian Support Program Requirement)
- `required_documents`: List of required documents (via Norwegian Support Program Document)

### 2. Norwegian Support Program Requirement (Child Table)

Stores individual requirements for a support program.

**Fields:**
- `requirement_title`: Title of the requirement
- `requirement_description`: Detailed description
- `is_mandatory`: Boolean indicating if requirement is mandatory

### 3. Norwegian Support Program Document (Child Table)

Stores information about required documents for a support program.

**Fields:**
- `document_name`: Name of the document
- `document_description`: Description of the document
- `is_mandatory`: Boolean indicating if document is mandatory
- `document_format`: Expected format (PDF, Word, Excel, Image, Any)
- `example_url`: Link to example or template

### 4. Kommune Newsletter

Stores municipal newsletter articles and announcements.

**Key Fields:**
- `kommune`: Municipality name
- `newsletter_date`: Publication date
- `title`: Article title
- `summary`: Short summary
- `full_content`: Full article content
- `is_highlighted`: Boolean for featured articles
- `category`: Article category
- `source_url`: Link to original article
- `tags`: Comma-separated tags

---

## API Endpoints

All endpoints are whitelisted and accessible via REST API at `/api/method/assist.api.<method_name>`.

### 1. Get Norwegian Support Programs

**Endpoint:** `get_norwegian_support_programs`

**Method:** GET/POST

**Parameters:**
- `entity_type` (optional): Filter by eligibility type
  - Values: `"private_person"`, `"company"`, `"housing"`, `"farm"`
- `provider` (optional): Filter by provider organization
  - Values: `"Enova"`, `"Kommune"`, `"Husbanken"`, `"Innovasjon Norge"`, etc.
- `program_type` (optional): Filter by program type
  - Values: `"Støtte"`, `"Fradrag"`, `"Lån"`, `"Garantier"`, `"Tilskudd"`
- `category` (optional): Filter by category
  - Values: `"Energi"`, `"Bygg og oppgradering"`, `"Klima og miljø"`, etc.
- `status` (optional): Filter by status (default: `"Active"`)

**Example:**
```javascript
frappe.call({
    method: "assist.api.get_norwegian_support_programs",
    args: {
        entity_type: "private_person",
        provider: "Enova",
        category: "Energi"
    },
    callback: function(r) {
        console.log(r.message.programs);
    }
});
```

**Returns:**
```json
{
    "success": true,
    "programs": [...],
    "count": 5,
    "filters_applied": {...},
    "message": "Found 5 support programs"
}
```

### 2. Get Enova Support Programs

**Endpoint:** `get_enova_support_programs`

**Method:** GET/POST

**Parameters:**
- `status` (optional): Filter by status (default: `"Active"`)

**Example:**
```javascript
frappe.call({
    method: "assist.api.get_enova_support_programs",
    callback: function(r) {
        console.log(r.message.programs);
    }
});
```

**Returns:**
Detailed information about all Enova programs including requirements and documents.

### 3. Get Kommune Support Programs

**Endpoint:** `get_kommune_support_programs`

**Method:** GET/POST

**Parameters:**
- `kommune` (optional): Specific kommune name
- `status` (optional): Filter by status (default: `"Active"`)

**Example:**
```javascript
frappe.call({
    method: "assist.api.get_kommune_support_programs",
    args: {
        kommune: "Oslo"
    },
    callback: function(r) {
        console.log(r.message.programs);
    }
});
```

### 4. Search Support Programs

**Endpoint:** `search_support_programs`

**Method:** GET/POST

**Parameters:**
- `search_term` (required): Keyword to search for
- `status` (optional): Filter by status (default: `"Active"`)

**Example:**
```javascript
frappe.call({
    method: "assist.api.search_support_programs",
    args: {
        search_term: "varmepumpe"
    },
    callback: function(r) {
        console.log(r.message.programs);
    }
});
```

### 5. Get Kommune Newsletters

**Endpoint:** `get_kommune_newsletters`

**Method:** GET/POST

**Parameters:**
- `kommune` (optional): Filter by specific kommune
- `is_highlighted` (optional): Filter by highlighted status
- `category` (optional): Filter by category
- `status` (optional): Filter by status (default: `"Published"`)
- `limit` (optional): Maximum number of articles (default: 20)

**Example:**
```javascript
frappe.call({
    method: "assist.api.get_kommune_newsletters",
    args: {
        kommune: "Oslo",
        is_highlighted: true
    },
    callback: function(r) {
        console.log(r.message.newsletters);
    }
});
```

### 6. Get Highlighted Kommune News

**Endpoint:** `get_highlighted_kommune_news`

**Method:** GET/POST

**Parameters:**
- `kommune` (optional): Filter by specific kommune
- `limit` (optional): Maximum number of articles (default: 10)

**Example:**
```javascript
frappe.call({
    method: "assist.api.get_highlighted_kommune_news",
    args: {
        limit: 5
    },
    callback: function(r) {
        console.log(r.message.newsletters);
    }
});
```

---

## MCP Server Tools

The following MCP tools are available for AI assistants:

### 1. get_support_programs

Query Norwegian support programs with flexible filtering.

**Parameters:**
- `entity_type`: private_person, company, housing, farm
- `provider`: Enova, Kommune, etc.
- `program_type`: Støtte, Fradrag, Lån, etc.
- `category`: Energi, Bygg og oppgradering, etc.

**Use Cases:**
- "Find all Enova støtte programs for private persons"
- "Show housing renovation grants"
- "What tax deductions are available for companies?"

### 2. get_enova_support_programs

Get all active Enova support programs with detailed information.

**Use Cases:**
- "What Enova support is available for heat pumps?"
- "Show all Enova solar panel grants"
- "List Enova business support programs"

### 3. search_norwegian_support

Search support programs by keyword.

**Parameters:**
- `search_term`: Keyword to search (Norwegian or English)

**Use Cases:**
- "Search for 'varmepumpe' support"
- "Find programs related to 'BSU'"
- "Search for 'byggesøknad' information"

---

## Sample Data

The system includes sample data for common Norwegian support programs:

### Enova Programs
1. **Varmepumpe til Bolig**: Heat pump installation support for homes
2. **Solceller til Bolig**: Solar panel installation support for homes
3. **Energieffektivisering i Bedrift**: Business energy efficiency support

### Husbanken Programs
4. **Grunnlån**: Basic loans for housing establishment and improvements

### Innovasjon Norge Programs
5. **Etablererstipend**: Startup grant for new businesses

### Landsbruksdirektoratet Programs
6. **Produksjonstilskudd**: Production subsidies for active farmers

### Skatteetaten Programs
7. **BSU (Boligsparing for Ungdom)**: Tax deduction for young home savers

### Kommune Programs
8. **Byggesøknad**: Building permit applications

---

## Use Cases

### 1. Finding Heat Pump Support
```javascript
// Search for heat pump support
frappe.call({
    method: "assist.api.search_support_programs",
    args: { search_term: "varmepumpe" },
    callback: function(r) {
        // Display programs with heat pump support
    }
});
```

### 2. Business Energy Support
```javascript
// Get energy programs for companies
frappe.call({
    method: "assist.api.get_norwegian_support_programs",
    args: {
        entity_type: "company",
        category: "Energi"
    },
    callback: function(r) {
        // Display business energy programs
    }
});
```

### 3. Agricultural Support
```javascript
// Get farm support programs
frappe.call({
    method: "assist.api.get_norwegian_support_programs",
    args: {
        entity_type: "farm",
        provider: "Landsbruksdirektoratet"
    },
    callback: function(r) {
        // Display farm programs
    }
});
```

### 4. Kommune News
```javascript
// Get highlighted news from Oslo kommune
frappe.call({
    method: "assist.api.get_highlighted_kommune_news",
    args: { kommune: "Oslo" },
    callback: function(r) {
        // Display highlighted news
    }
});
```

---

## Integration

### With Existing Features

The Norwegian Support Programs Index integrates with existing Assist features:

1. **Kommune Applications**: Links to the existing `submit_kommune_application` function for building permits
2. **Skatteetaten Integration**: Complements the existing `interact_with_skatteetaten` function
3. **MCP Server**: Tools are registered with the MCP server for AI assistant access

### External Services

The system can integrate with:

- **Enova.no**: Official Enova website for up-to-date program information
- **Kommune websites**: Municipal websites for local programs
- **DOGA.no**: Design and Architecture Norway (as mentioned in requirements)
- **Skatteetaten.no**: Tax authority for fradrag information

---

## Future Enhancements

Potential improvements to the system:

1. **Automatic Data Updates**: Scrape official websites for program updates
2. **Application Tracking**: Track application status for submitted programs
3. **Eligibility Calculator**: Calculate eligibility based on user criteria
4. **Document Templates**: Provide downloadable templates for required documents
5. **Notification System**: Alert users about:
   - New programs matching their criteria
   - Upcoming deadlines
   - Program changes
6. **Multi-language Support**: Support both Norwegian Bokmål and Nynorsk
7. **API Integration**: Direct API integration with:
   - Enova application portal
   - Kommune digital services
   - Altinn for government forms

---

## Testing

### Creating Test Data

```python
# Create a support program
program = frappe.get_doc({
    "doctype": "Norwegian Support Program",
    "program_name": "Test Enova Støtte",
    "provider": "Enova",
    "program_type": "Støtte",
    "category": "Energi",
    "status": "Active",
    "eligible_for_private_person": 1,
    "short_description": "Test support program"
}).insert()
```

### Running Tests

```bash
# Run all tests for the module
bench --site your-site-name run-tests --app assist --module assist.assist_tools.doctype.norwegian_support_program.test_norwegian_support_program

# Run specific test
bench --site your-site-name run-tests --app assist --doctype "Norwegian Support Program"
```

---

## Maintenance

### Adding New Programs

1. Navigate to: Desk → Assist Tools → Norwegian Support Program
2. Click "New"
3. Fill in program details:
   - Program name
   - Provider
   - Eligibility checkboxes
   - Financial information
   - Requirements (child table)
   - Required documents (child table)
4. Save

### Updating Programs

- Programs can be updated manually or via API
- Set status to "Expired" for programs that are no longer available
- Use "Inactive" for temporarily unavailable programs
- Use "Upcoming" for announced but not yet available programs

### Bulk Import

Use the fixtures file for bulk importing:

```bash
bench --site your-site-name import-doc assist/fixtures/norwegian_support_programs.json
```

---

## References

- [Enova.no](https://www.enova.no/) - Energy and climate support
- [Husbanken.no](https://husbanken.no/) - Housing bank
- [Innovasjon Norge](https://www.innovasjonnorge.no/) - Business innovation
- [Skatteetaten.no](https://www.skatteetaten.no/) - Tax authority
- [Landbruksdirektoratet.no](https://www.landbruksdirektoratet.no/) - Agricultural directorate
- [DOGA.no](https://doga.no/) - Design and Architecture Norway

---

## Support

For issues or questions:
- Email: kontakt@drivstoffapp.no
- Repository: https://github.com/samletnorge/assist
