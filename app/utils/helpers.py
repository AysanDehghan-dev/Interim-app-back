import re
from datetime import datetime
from typing import Dict, List, Optional, Union, Any


def paginate_results(results: List[Dict], total_count: int, page: int, limit: int) -> Dict:
    """Create pagination metadata for results"""
    total_pages = (total_count + limit - 1) // limit  # Ceiling division
    
    return {
        "data": results,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "limit": limit,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }


def validate_email_format(email: str) -> bool:
    """Validate email format using regex"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def clean_phone_number(phone: str) -> Optional[str]:
    """Clean and format phone number"""
    if not phone:
        return None
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Must have at least 10 digits
    if len(digits) < 10:
        return None
    
    return digits


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object to string"""
    if not dt:
        return ""
    
    return dt.strftime(format_str)


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to integer"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to max_length with optional suffix"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text"""
    if not text:
        return ""
    
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special characters
    slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces and multiple hyphens
    
    return slug


def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result