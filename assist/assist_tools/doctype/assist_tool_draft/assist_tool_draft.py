# Copyright (c) 2026, samletnorge and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class AssistToolDraft(Document):
    def validate(self):
        """Validate the tool draft before saving."""
        if not self.created_by:
            self.created_by = frappe.session.user
        self.modified_by = frappe.session.user
    
    def execute_tool(self, context=None):
        """
        Execute the tool with the given context.
        This method dynamically executes the tool based on its configuration.
        
        Args:
            context: Dictionary containing parameter values
        
        Returns:
            Result of the tool execution
        """
        if not self.enabled:
            return {
                "success": False,
                "message": "Tool is disabled"
            }
        
        # Increment usage count
        self.usage_count = (self.usage_count or 0) + 1
        self.save(ignore_permissions=True)
        
        context = context or {}
        
        # Process prompt template with context
        prompt = self.prompt_template
        for key, value in context.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
        
        # Execute based on action type
        if self.action_type == "Create Document":
            return self._create_document(context)
        elif self.action_type == "Update Document":
            return self._update_document(context)
        elif self.action_type == "API Call":
            return self._api_call(context)
        elif self.action_type == "Custom Code":
            return self._execute_custom_code(context)
        else:
            return {
                "success": False,
                "message": "Unknown action type"
            }
    
    def _create_document(self, context):
        """Create a document based on tool configuration."""
        try:
            if not self.target_doctype:
                return {"success": False, "message": "Target DocType not specified"}
            
            # Build document from context
            doc_dict = {"doctype": self.target_doctype}
            for param in self.parameters:
                if param.parameter_name in context:
                    doc_dict[param.parameter_name] = context[param.parameter_name]
            
            doc = frappe.get_doc(doc_dict)
            doc.insert()
            
            return {
                "success": True,
                "message": f"Created {self.target_doctype}",
                "document": doc.name
            }
        except Exception as e:
            frappe.log_error(f"Tool execution error: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def _update_document(self, context):
        """Update a document based on tool configuration."""
        try:
            if not self.target_doctype:
                return {"success": False, "message": "Target DocType not specified"}
            
            doc_name = context.get("name")
            if not doc_name:
                return {"success": False, "message": "Document name not provided"}
            
            doc = frappe.get_doc(self.target_doctype, doc_name)
            
            for param in self.parameters:
                if param.parameter_name in context and param.parameter_name != "name":
                    setattr(doc, param.parameter_name, context[param.parameter_name])
            
            doc.save()
            
            return {
                "success": True,
                "message": f"Updated {self.target_doctype}",
                "document": doc.name
            }
        except Exception as e:
            frappe.log_error(f"Tool execution error: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def _api_call(self, context):
        """Make an API call based on tool configuration."""
        try:
            import requests
            
            if not self.api_endpoint:
                return {"success": False, "message": "API endpoint not specified"}
            
            response = requests.post(self.api_endpoint, json=context)
            response.raise_for_status()
            
            return {
                "success": True,
                "message": "API call successful",
                "response": response.json()
            }
        except Exception as e:
            frappe.log_error(f"Tool execution error: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def _execute_custom_code(self, context):
        """Execute custom Python code."""
        try:
            if not self.custom_code:
                return {"success": False, "message": "No custom code specified"}
            
            # Create a safe execution environment
            exec_globals = {
                "frappe": frappe,
                "context": context,
                "result": None,
            }
            
            exec(self.custom_code, exec_globals)
            
            return {
                "success": True,
                "message": "Custom code executed successfully",
                "result": exec_globals.get("result")
            }
        except Exception as e:
            frappe.log_error(f"Tool execution error: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }


@frappe.whitelist()
def execute_tool(tool_name, context=None):
    """
    API endpoint to execute a tool by name.
    
    Args:
        tool_name: Name of the tool to execute
        context: JSON string or dict containing parameter values
    
    Returns:
        Result of the tool execution
    """
    if isinstance(context, str):
        context = json.loads(context)
    
    tool = frappe.get_doc("Assist Tool Draft", tool_name)
    return tool.execute_tool(context)


@frappe.whitelist()
def get_available_tools(category=None):
    """
    Get list of available tools, optionally filtered by category.
    
    Args:
        category: Optional category filter
    
    Returns:
        List of enabled tools
    """
    filters = {"enabled": 1}
    if category:
        filters["category"] = category
    
    tools = frappe.get_all(
        "Assist Tool Draft",
        filters=filters,
        fields=["name", "tool_name", "tool_description", "category", "usage_count"]
    )
    
    return tools
