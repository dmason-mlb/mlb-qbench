"""Filter validation models for secure input sanitization."""

import re
from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class FilterableField(str, Enum):
    """Allowed filterable fields - whitelist approach for security."""
    
    # Test metadata fields
    TEST_TYPE = "testType"
    PRIORITY = "priority" 
    PLATFORMS = "platforms"
    TAGS = "tags"
    FOLDER_STRUCTURE = "folderStructure"
    
    # JIRA related fields
    JIRA_KEY = "jiraKey"
    
    # Test execution fields  
    STATUS = "status"
    
    # Date fields (if needed)
    INGESTED_AT = "ingested_at"


class FilterOperator(str, Enum):
    """Allowed filter operators."""
    
    EQUALS = "eq"
    IN = "in" 
    NOT_IN = "not_in"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"


class FilterValue(BaseModel):
    """A single filter value with validation."""
    
    field: FilterableField = Field(..., description="Field to filter on")
    operator: FilterOperator = Field(FilterOperator.EQUALS, description="Filter operator")
    value: Union[str, int, List[str], List[int]] = Field(..., description="Filter value")
    
    @field_validator('value')
    @classmethod
    def validate_filter_value(cls, v: Any) -> Any:
        """Validate filter values for security."""
        if isinstance(v, str):
            # Sanitize string values
            if len(v.strip()) == 0:
                raise ValueError("Filter value cannot be empty")
            if len(v) > 100:  # Reasonable length limit
                raise ValueError("Filter value too long (max 100 characters)")
            # Check for potentially dangerous characters
            if re.search(r'[<>&"\']', v):
                raise ValueError("Filter value contains potentially dangerous characters")
            return v.strip()
        
        elif isinstance(v, int):
            # Validate integer ranges
            if v < -1000000 or v > 1000000:  # Reasonable bounds
                raise ValueError("Integer filter value out of range")
            return v
        
        elif isinstance(v, list):
            if len(v) == 0:
                raise ValueError("Filter list cannot be empty")
            if len(v) > 50:  # Reasonable list size limit
                raise ValueError("Filter list too long (max 50 items)")
            
            # Validate each item in list
            validated_items = []
            for item in v:
                if isinstance(item, str):
                    if len(item.strip()) == 0:
                        continue  # Skip empty strings
                    if len(item) > 100:
                        raise ValueError("Filter list item too long (max 100 characters)")
                    if re.search(r'[<>&"\']', item):
                        raise ValueError("Filter list item contains dangerous characters")
                    validated_items.append(item.strip())
                elif isinstance(item, int):
                    if item < -1000000 or item > 1000000:
                        raise ValueError("Integer filter list item out of range")
                    validated_items.append(item)
                else:
                    raise ValueError(f"Invalid filter list item type: {type(item)}")
            
            if len(validated_items) == 0:
                raise ValueError("Filter list has no valid items")
            return validated_items
        
        else:
            raise ValueError(f"Invalid filter value type: {type(v)}")
    
    @model_validator(mode='after')
    def validate_field_value_compatibility(self) -> 'FilterValue':
        """Validate that field and value types are compatible."""
        field = self.field
        value = self.value
        operator = self.operator
        
        # Define expected types for each field
        string_fields = {
            FilterableField.TEST_TYPE,
            FilterableField.PRIORITY,
            FilterableField.FOLDER_STRUCTURE,
            FilterableField.JIRA_KEY,
            FilterableField.STATUS
        }
        
        list_fields = {
            FilterableField.PLATFORMS,
            FilterableField.TAGS
        }
        
        # Validate field-value compatibility
        if field in string_fields:
            if operator in [FilterOperator.IN, FilterOperator.NOT_IN]:
                if not isinstance(value, list):
                    raise ValueError(f"Field {field} with operator {operator} requires list value")
            else:
                if not isinstance(value, (str, int)):  # Allow int for priority field
                    raise ValueError(f"Field {field} requires string or int value")
        
        elif field in list_fields:
            # List fields can be filtered with single values or lists
            if operator in [FilterOperator.EQUALS, FilterOperator.CONTAINS]:
                if not isinstance(value, (str, list)):
                    raise ValueError(f"Field {field} requires string or list value")
            elif operator in [FilterOperator.IN, FilterOperator.NOT_IN]:
                if not isinstance(value, list):
                    raise ValueError(f"Field {field} with operator {operator} requires list value")
        
        # Additional JIRA key validation
        if field == FilterableField.JIRA_KEY and isinstance(value, str):
            jira_pattern = r'^[A-Z][A-Z0-9]*-\d+$'
            if not re.match(jira_pattern, value):
                raise ValueError(f"Invalid JIRA key format: {value}")
        
        return self


class ValidatedFilters(BaseModel):
    """Container for validated filters."""
    
    filters: List[FilterValue] = Field(default_factory=list, description="List of validated filters")
    
    @field_validator('filters')
    @classmethod  
    def validate_filter_count(cls, v: List[FilterValue]) -> List[FilterValue]:
        """Validate filter count for DoS protection."""
        if len(v) > 20:  # Reasonable limit on number of filters
            raise ValueError("Too many filters (max 20)")
        return v
    
    def to_qdrant_filter_dict(self) -> Optional[Dict[str, Any]]:
        """Convert validated filters to dictionary format for build_filter."""
        if not self.filters:
            return None
        
        filter_dict = {}
        
        for filter_value in self.filters:
            field = filter_value.field.value
            operator = filter_value.operator
            value = filter_value.value
            
            # Handle different operators
            if operator == FilterOperator.EQUALS:
                filter_dict[field] = value
            elif operator == FilterOperator.IN:
                # For IN operator, treat as list value
                filter_dict[field] = value if isinstance(value, list) else [value]
            elif operator == FilterOperator.CONTAINS:
                # For CONTAINS, we'll handle this in build_filter with special logic
                filter_dict[f"{field}__contains"] = value
            # Add more operators as needed
        
        return filter_dict if filter_dict else None


def validate_and_sanitize_filters(filters: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Validate and sanitize filter input.
    
    Args:
        filters: Raw filter dictionary from user input
        
    Returns:
        Sanitized filter dictionary safe for Qdrant operations
        
    Raises:
        ValueError: If validation fails
    """
    if not filters:
        return None
    
    try:
        # Convert old-style dict to new FilterValue format
        filter_values = []
        
        for field_name, field_value in filters.items():
            # Determine operator and actual field name
            if field_name.endswith("__contains"):
                actual_field_name = field_name.replace("__contains", "")
                try:
                    filterable_field = FilterableField(actual_field_name)
                except ValueError:
                    raise ValueError(f"Invalid filter field: {actual_field_name}")
                operator = FilterOperator.CONTAINS
            else:
                # Check if field is allowed
                try:
                    filterable_field = FilterableField(field_name)
                except ValueError:
                    raise ValueError(f"Invalid filter field: {field_name}")
                
                # Determine operator based on value type
                if isinstance(field_value, list):
                    operator = FilterOperator.IN
                else:
                    operator = FilterOperator.EQUALS
            
            # Create validated filter
            filter_values.append(FilterValue(
                field=filterable_field,
                operator=operator,
                value=field_value
            ))
        
        # Validate the complete filter set
        validated = ValidatedFilters(filters=filter_values)
        
        # Return sanitized dictionary
        return validated.to_qdrant_filter_dict()
        
    except Exception as e:
        raise ValueError(f"Filter validation failed: {str(e)}")


# Priority validation patterns
VALID_PRIORITIES = {"Critical", "High", "Medium", "Low"}
VALID_TEST_TYPES = {"Functional", "API", "Integration", "Unit", "Performance"}
VALID_PLATFORMS = {"web", "mobile", "api", "desktop", "ios", "android"}

def validate_priority_value(priority: str) -> str:
    """Validate priority value against allowed values."""
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority: {priority}. Must be one of {VALID_PRIORITIES}")
    return priority

def validate_test_type_value(test_type: str) -> str:
    """Validate test type value against allowed values.""" 
    if test_type not in VALID_TEST_TYPES:
        raise ValueError(f"Invalid test type: {test_type}. Must be one of {VALID_TEST_TYPES}")
    return test_type

def validate_platform_values(platforms: List[str]) -> List[str]:
    """Validate platform values against allowed values."""
    for platform in platforms:
        if platform not in VALID_PLATFORMS:
            raise ValueError(f"Invalid platform: {platform}. Must be one of {VALID_PLATFORMS}")
    return platforms