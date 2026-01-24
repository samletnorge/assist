#!/usr/bin/env python3
"""
Simple validation script for Norwegian Support Programs feature.
This script validates the structure and basic functionality without requiring a running Frappe instance.
"""

import json
import os
import sys


def validate_json_structure(file_path, required_fields):
    """Validate JSON file has required fields."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing required field '{field}' in {file_path}")
                return False
        
        print(f"✅ {os.path.basename(file_path)} - Valid structure")
        return True
    except Exception as e:
        print(f"❌ Error validating {file_path}: {e}")
        return False


def validate_doctype_structure():
    """Validate all doctype JSON structures."""
    print("\n=== Validating DocType Structures ===\n")
    
    base_path = "assist/assist_tools/doctype"
    
    all_valid = True
    
    # Validate Norwegian Support Program
    nsp_required = ["doctype", "name", "fields", "permissions"]
    result = validate_json_structure(
        f"{base_path}/norwegian_support_program/norwegian_support_program.json",
        nsp_required
    )
    all_valid = all_valid and result
    
    # Validate child tables
    child_required = ["doctype", "name", "fields", "istable"]
    result = validate_json_structure(
        f"{base_path}/norwegian_support_program_requirement/norwegian_support_program_requirement.json",
        child_required
    )
    all_valid = all_valid and result
    
    result = validate_json_structure(
        f"{base_path}/norwegian_support_program_document/norwegian_support_program_document.json",
        child_required
    )
    all_valid = all_valid and result
    
    # Validate Kommune Newsletter
    result = validate_json_structure(
        f"{base_path}/kommune_newsletter/kommune_newsletter.json",
        nsp_required
    )
    all_valid = all_valid and result
    
    return all_valid


def validate_fixtures():
    """Validate fixture data."""
    print("\n=== Validating Fixture Data ===\n")
    
    fixture_path = "assist/fixtures/norwegian_support_programs.json"
    
    try:
        with open(fixture_path, 'r') as f:
            programs = json.load(f)
        
        if not isinstance(programs, list):
            print(f"❌ Fixture should be a list of programs")
            return False
        
        print(f"✅ Found {len(programs)} sample programs in fixtures")
        
        # Validate each program has required fields
        required_fields = ["doctype", "program_name", "provider", "program_type", "status"]
        for i, program in enumerate(programs):
            for field in required_fields:
                if field not in program:
                    print(f"❌ Program {i+1} missing field '{field}'")
                    return False
        
        print(f"✅ All programs have required fields")
        
        # Count by provider
        providers = {}
        for program in programs:
            provider = program.get("provider", "Unknown")
            providers[provider] = providers.get(provider, 0) + 1
        
        print(f"\n📊 Programs by provider:")
        for provider, count in sorted(providers.items()):
            print(f"   - {provider}: {count}")
        
        return True
    except Exception as e:
        print(f"❌ Error validating fixtures: {e}")
        return False


def validate_python_syntax():
    """Validate Python files for syntax errors."""
    print("\n=== Validating Python Syntax ===\n")
    
    python_files = [
        "assist/assist_tools/doctype/norwegian_support_program/norwegian_support_program.py",
        "assist/assist_tools/doctype/norwegian_support_program_requirement/norwegian_support_program_requirement.py",
        "assist/assist_tools/doctype/norwegian_support_program_document/norwegian_support_program_document.py",
        "assist/assist_tools/doctype/kommune_newsletter/kommune_newsletter.py",
    ]
    
    all_valid = True
    for py_file in python_files:
        try:
            with open(py_file, 'r') as f:
                compile(f.read(), py_file, 'exec')
            print(f"✅ {os.path.basename(py_file)} - Valid syntax")
        except SyntaxError as e:
            print(f"❌ {os.path.basename(py_file)} - Syntax error: {e}")
            all_valid = False
    
    return all_valid


def validate_api_endpoints():
    """Check that API endpoints are defined."""
    print("\n=== Validating API Endpoints ===\n")
    
    try:
        with open("assist/api.py", 'r') as f:
            api_content = f.read()
        
        expected_endpoints = [
            "get_norwegian_support_programs",
            "get_enova_support_programs",
            "get_kommune_support_programs",
            "search_support_programs",
            "get_kommune_newsletters",
            "get_highlighted_kommune_news"
        ]
        
        for endpoint in expected_endpoints:
            if f"def {endpoint}" in api_content:
                print(f"✅ API endpoint: {endpoint}")
            else:
                print(f"❌ Missing API endpoint: {endpoint}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error validating API: {e}")
        return False


def validate_mcp_tools():
    """Check that MCP tools are defined."""
    print("\n=== Validating MCP Server Tools ===\n")
    
    try:
        with open("assist/mcp_server/server.py", 'r') as f:
            mcp_content = f.read()
        
        expected_tools = [
            "get_support_programs",
            "get_enova_support_programs",
            "search_norwegian_support"
        ]
        
        for tool in expected_tools:
            if f"def {tool}" in mcp_content:
                print(f"✅ MCP tool: {tool}")
            else:
                print(f"❌ Missing MCP tool: {tool}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error validating MCP tools: {e}")
        return False


def main():
    """Run all validations."""
    print("=" * 60)
    print("Norwegian Support Programs - Validation Script")
    print("=" * 60)
    
    results = []
    
    # Change to repo root
    if os.path.exists("assist"):
        os.chdir(".")
    elif os.path.exists("../assist"):
        os.chdir("..")
    
    results.append(("DocType Structures", validate_doctype_structure()))
    results.append(("Fixture Data", validate_fixtures()))
    results.append(("Python Syntax", validate_python_syntax()))
    results.append(("API Endpoints", validate_api_endpoints()))
    results.append(("MCP Tools", validate_mcp_tools()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60 + "\n")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All validations passed!")
        print("=" * 60)
        return 0
    else:
        print("⚠️  Some validations failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
