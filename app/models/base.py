from datetime import datetime
from bson.objectid import ObjectId
import re

from app.utils.db import (
    count_documents,
    find_by_id,
    find_many,
    find_one,
    insert_one,
    update_one,
)
from app.models.exceptions import ValidationError


class BaseModel:
    """Base model class with common functionality"""
    
    COLLECTION = None  # Must be defined in subclasses
    
    @classmethod
    def _validate_object_id(cls, value, field_name):
        """Validate and convert to ObjectId"""
        if not value:
            return None
            
        if isinstance(value, ObjectId):
            return value
            
        try:
            return ObjectId(value)
        except Exception:
            raise ValidationError(f"Invalid {field_name}: must be a valid ObjectId")
    
    @classmethod
    def _validate_email(cls, email):
        """Validate email format"""
        if not email:
            raise ValidationError("Email is required")
            
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Invalid email format")
        
        return email.lower().strip()
    
    @classmethod
    def _add_timestamps(cls, data, is_update=False):
        """Add created_at and updated_at timestamps"""
        now = datetime.utcnow()
        
        if not is_update and "created_at" not in data:
            data["created_at"] = now
            
        data["updated_at"] = now
        return data
    
    @classmethod
    def find_by_id(cls, item_id):
        """Find item by ID"""
        if not cls.COLLECTION:
            raise NotImplementedError("COLLECTION must be defined")
        return find_by_id(cls.COLLECTION, item_id)
    
    @classmethod
    def count_all(cls, query=None):
        """Count all items matching query"""
        if not cls.COLLECTION:
            raise NotImplementedError("COLLECTION must be defined")
        return count_documents(cls.COLLECTION, query or {})