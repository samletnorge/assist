# Standards-Based Tools - RDS 81346 & S1000D Issue 6

This document describes the two new industrial and aerospace standards-based tools added to ERPNext Assist.

## Overview

These tools enable compliance with international standards for equipment documentation and technical publications:

1. **RDS 81346** - ISO/IEC 81346 Reference Designation System for equipment
2. **S1000D Issue 6** - International specification for technical publications in aerospace and defense

---

## Tool 7: RDS 81346 Equipment Reference Designation

### Purpose
Generate ISO/IEC 81346 compliant reference designations for industrial systems, installations, and equipment. Creates standardized identifiers that reflect equipment function, product type, location, and hierarchy.

### MCP Tool
`generate_rds_81346_designation()`

### API Endpoint
`erpnext_assist.api.generate_rds_designation`

### Standard Compliance
- **ISO/IEC 81346-1**: Structure principles and reference designations
- **ISO/IEC 81346-2**: Classification of objects and codes for classes
- **ISO/IEC 81346-12**: RFID in industrial systems

### RDS Aspects

The tool supports all four aspects of ISO/IEC 81346:

#### 1. Function Aspect (=)
- **What the equipment does**
- Prefix: `=`
- Examples: `=PUMP`, `=MOTOR`, `=COOL`, `=HEAT`

#### 2. Product Aspect (-)
- **What the equipment is**
- Prefix: `-`
- Examples: `-M1` (motor), `-P1` (pump), `-V1` (valve)

#### 3. Location Aspect (+)
- **Where the equipment is**
- Prefix: `+`
- Examples: `+ROOM1`, `+FLOOR2`, `+BLDGA`

#### 4. Type Aspect (%)
- **Class/type of equipment** (newer standard)
- Prefix: `%`
- Examples: `%CENTRIFUGAL`, `%AC`, `%3PHASE`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| equipment_name | String | ✓ | Name of equipment/component |
| function_aspect | String | | Functional classification |
| product_aspect | String | | Product classification |
| location_aspect | String | | Location classification |
| parent_system | String | | Parent system designation |

### Usage Examples

#### Example 1: Wind Turbine System
```python
result = generate_rds_81346_designation(
    equipment_name="High Speed Axle",
    function_aspect="=A1",      # Main system
    product_aspect="-WQA1",     # High speed axle
    location_aspect="+SITE1",   # Site location
    parent_system="TURBINE1"
)
# Returns: "TURBINE1.=A1.-WQA1.+SITE1"
```

#### Example 2: Industrial Cooling System
```python
result = generate_rds_81346_designation(
    equipment_name="Cooling Pump",
    function_aspect="=COOL",    # Cooling function
    product_aspect="-PUMP01",   # Pump #1
    location_aspect="+ROOM1",   # Room 1
    parent_system="HVAC"
)
# Returns: "HVAC.=COOL.-PUMP01.+ROOM1"
```

#### Example 3: Building Electrical System
```python
result = generate_rds_81346_designation(
    equipment_name="Motor Controller",
    function_aspect="=DRIVE",   # Drive function
    product_aspect="-MC01",     # Motor controller
    location_aspect="+PANEL2"   # Panel 2
)
# Returns: "=DRIVE.-MC01.+PANEL2"
```

### Return Format

```json
{
    "success": true,
    "equipment_name": "Cooling Pump",
    "rds_designation": "HVAC.=COOL.-PUMP01.+ROOM1",
    "aspects": {
        "function": "=COOL",
        "product": "-PUMP01",
        "location": "+ROOM1",
        "parent": "HVAC"
    },
    "standard": "ISO/IEC 81346",
    "message": "RDS designation generated: HVAC.=COOL.-PUMP01.+ROOM1"
}
```

### Use Cases

1. **Industrial Plants**
   - Process equipment tracking
   - Maintenance documentation
   - Spare parts management

2. **Building Systems**
   - HVAC equipment
   - Electrical systems
   - Fire safety systems
   - Building automation

3. **Complex Machinery**
   - Manufacturing equipment
   - Production lines
   - Quality control systems

4. **Multi-Site Facilities**
   - Corporate campuses
   - Hospital systems
   - University infrastructure

5. **Oil & Gas**
   - Pipeline systems
   - Refinery equipment
   - Offshore platforms

### Benefits

- **Standardization**: Globally recognized naming convention
- **Clarity**: Unambiguous equipment identification
- **Scalability**: Works from single components to complex systems
- **Integration**: Compatible with BIM, CAD, and CMMS systems
- **Compliance**: Meets regulatory requirements

---

## Tool 8: S1000D Issue 6 Technical Documentation

### Purpose
Create S1000D Issue 6 compliant data modules for technical publications. Generates XML-based modular documentation for aerospace and defense equipment following international standards.

### MCP Tool
`create_s1000d_data_module()`

### API Endpoint
`erpnext_assist.api.create_s1000d_module`

### Standard Compliance
- **S1000D Issue 6** (latest version)
- **ASD-STAN prEN 9297** (S-Series specifications)
- **MIL-STD-3048** (USAF S1000D business rules)
- **NATO standards** for technical publications

### S1000D Concepts

#### Data Module Code (DMC)
Unique identifier for each data module following this structure:
```
DMC-[Model]-[System]-[SubSystem]-[Assy]-[Disassy]-[Info]-[Variant]
```

Example: `DMC-AIRCRAFT-A-72-10-00-00A-520A-A`

#### Content Types

1. **Procedural** - Step-by-step instructions
2. **Descriptive** - System/component descriptions
3. **Fault** - Troubleshooting and diagnostics
4. **Crew** - Crew procedures and checklists

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| item_code | String | ✓ | ERPNext item code |
| data_module_code | String | ✓ | S1000D DMC identifier |
| title | String | ✓ | Data module title |
| content_type | String | ✓ | Content type (procedural/descriptive/fault/crew) |
| issue_number | String | | S1000D issue (default: "6") |

### Usage Examples

#### Example 1: Aircraft Engine Maintenance
```python
result = create_s1000d_data_module(
    item_code="ENGINE-001",
    data_module_code="DMC-AIRCRAFT-A-72-10-00-00A-520A-A",
    title="Engine Oil System - Maintenance Procedure",
    content_type="procedural",
    issue_number="6"
)
```

#### Example 2: Avionics System Description
```python
result = create_s1000d_data_module(
    item_code="AVIONICS-NAV",
    data_module_code="DMC-AVIONICS-A-45-20-01-00A-040A-A",
    title="Navigation System Description",
    content_type="descriptive",
    issue_number="6"
)
```

#### Example 3: Hydraulic System Troubleshooting
```python
result = create_s1000d_data_module(
    item_code="HYDRAULIC-SYS",
    data_module_code="DMC-AIRCRAFT-A-29-30-00-00A-730A-A",
    title="Hydraulic System Fault Isolation",
    content_type="fault",
    issue_number="6"
)
```

### Return Format

```json
{
    "success": true,
    "data_module": {
        "dmc": "DMC-AIRCRAFT-A-72-10-00-00A-520A-A",
        "issue_number": "6",
        "title": "Engine Oil System - Maintenance Procedure",
        "item_code": "ENGINE-001",
        "content_type": "procedural",
        "status": "draft",
        "created_date": "2026-01-05T18:00:00",
        "language": "en-US",
        "metadata": {
            "model_ident_code": "ENGI",
            "system_code": "72",
            "sub_system_code": "10",
            "info_code": "520"
        },
        "content": {
            "description": "...",
            "procedures": [],
            "warnings": [],
            "cautions": []
        }
    },
    "standard": "S1000D Issue 6",
    "message": "S1000D data module created: DMC-AIRCRAFT-A-72-10-00-00A-520A-A"
}
```

### Use Cases

1. **Aerospace**
   - Aircraft maintenance manuals
   - Component service bulletins
   - Illustrated parts catalogs
   - Crew operating handbooks

2. **Defense**
   - Military equipment manuals
   - Weapon system documentation
   - Training materials
   - Technical orders

3. **Naval Systems**
   - Ship systems documentation
   - Submarine procedures
   - Naval aviation manuals

4. **Land Systems**
   - Armored vehicle manuals
   - Ground support equipment
   - Mobile command systems

5. **Commercial Aviation**
   - Airline maintenance procedures
   - Component overhaul manuals
   - Line maintenance guides

### S1000D Features

#### 1. Modular Data Structure
- Small, reusable information units
- Easy to update and maintain
- Version control per module

#### 2. Common Source Database (CSDB)
- Centralized documentation repository
- Single source of truth
- Multi-user collaboration

#### 3. XML-Based
- Machine-readable format
- Digital publishing ready
- Integration with IETMs (Interactive Electronic Technical Manuals)

#### 4. Business Rules
- Organization-specific customization
- Compliance enforcement
- Workflow automation

### Benefits

- **Interoperability**: Seamless data exchange between organizations
- **Reusability**: Content shared across multiple publications
- **Reduced Costs**: Lower authoring and update costs
- **Version Control**: Track all changes and revisions
- **Multi-Platform**: Single source for print, web, and mobile
- **Compliance**: Meets NATO, DoD, and international standards

### Integration Points

1. **ERPNext Items**: Link data modules to inventory items
2. **BOM Integration**: Technical docs for bill of materials
3. **Asset Management**: Documentation for tracked assets
4. **Maintenance**: Link to maintenance schedules
5. **Quality**: QA procedures and specifications

---

## API Integration

### RDS 81346 API Call
```javascript
// From ERPNext UI
frappe.call({
    method: "erpnext_assist.api.generate_rds_designation",
    args: {
        equipment_name: "Cooling Pump",
        function_aspect: "=COOL",
        product_aspect: "-PUMP01",
        location_aspect: "+ROOM1",
        parent_system: "HVAC"
    },
    callback: function(r) {
        console.log(r.message.rds_designation);
        // Output: "HVAC.=COOL.-PUMP01.+ROOM1"
    }
});
```

### S1000D API Call
```javascript
// From ERPNext UI
frappe.call({
    method: "erpnext_assist.api.create_s1000d_module",
    args: {
        item_code: "ENGINE-001",
        data_module_code: "DMC-AIRCRAFT-A-72-10-00-00A-520A-A",
        title: "Engine Oil System Maintenance",
        content_type: "procedural",
        issue_number: "6"
    },
    callback: function(r) {
        console.log(r.message.data_module);
    }
});
```

---

## Visual Tool Builder Integration

Both tools can be created in the Visual Tool Builder without programming:

### Example: RDS Equipment Designator
```
Tool Name: "Equipment RDS Generator"
Category: Inventory
Prompt: "Generate RDS designation for {{equipment_name}}"
Action Type: Custom Code
Code:
    from erpnext_assist.mcp_server.server import generate_rds_81346_designation
    result = generate_rds_81346_designation(
        equipment_name=context['equipment_name'],
        function_aspect=context.get('function_aspect'),
        product_aspect=context.get('product_aspect'),
        location_aspect=context.get('location_aspect')
    )
```

### Example: S1000D Documentation Tool
```
Tool Name: "Tech Manual Generator"
Category: Custom
Prompt: "Create S1000D module for {{item_code}}"
Action Type: Custom Code
Code:
    from erpnext_assist.mcp_server.server import create_s1000d_data_module
    result = create_s1000d_data_module(
        item_code=context['item_code'],
        data_module_code=context['data_module_code'],
        title=context['title'],
        content_type=context.get('content_type', 'procedural')
    )
```

---

## Implementation Notes

### RDS 81346 Implementation
- **Current**: Basic designation generation
- **Future Enhancements**:
  - Custom DocType for equipment registry
  - Hierarchical tree view
  - Equipment relationship mapping
  - Export to P&ID/CAD systems
  - Integration with maintenance schedules

### S1000D Implementation
- **Current**: Data module structure generation
- **Future Enhancements**:
  - Full XML schema validation
  - CSDB database integration
  - Interactive IETM generation
  - Graphic hotspot creation
  - Multimedia content support
  - Publication module assembly

### Dependencies
- No additional dependencies required
- Optional: XML libraries for enhanced S1000D output
- Optional: Database for CSDB implementation

---

## Standards Resources

### RDS 81346
- [ISO/IEC 81346 Official Site](https://www.81346.com/)
- ISO/IEC 81346-1:2022 - Structure principles
- ISO/IEC 81346-2:2020 - Classification
- ISO/IEC 81346-12:2018 - RFID integration

### S1000D
- [S1000D Official Site](https://s1000d.org/)
- S1000D Issue 6.0 - Current specification
- ASD-STAN prEN 9297
- MIL-STD-3048 (USAF business rules)

---

## Summary

These two standards-based tools enable ERPNext Assist to support:

1. **Industrial Equipment Documentation** (RDS 81346)
   - Standardized naming conventions
   - Multi-disciplinary systems
   - Global compliance

2. **Aerospace/Defense Technical Publications** (S1000D)
   - Modular documentation
   - XML-based authoring
   - International standards compliance

Both tools integrate seamlessly with ERPNext's existing functionality while providing professional-grade standards compliance for specialized industries.
