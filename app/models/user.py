from datetime import datetime
from bson.objectid import ObjectId

from app.utils.db import find_one, insert_one, update_one
from app.utils.security import hash_password, verify_password
from app.models.base import BaseModel
from app.models.exceptions import ValidationError


class User(BaseModel):
    """User model class"""
    
    COLLECTION = "users"
    
    @classmethod
    def create(cls, user_data):
        """Create a new user"""
        # Validate required fields
        if not user_data.get("email"):
            raise ValidationError("Email is required")
        if not user_data.get("password"):
            raise ValidationError("Password is required")
        if not user_data.get("first_name"):
            raise ValidationError("First name is required")
        if not user_data.get("last_name"):
            raise ValidationError("Last name is required")
        
        # Validate email format
        user_data["email"] = cls._validate_email(user_data["email"])
        
        # Check if email already exists
        if cls.find_by_email(user_data["email"]):
            raise ValidationError("Email already exists")
        
        # Hash password
        user_data["password"] = hash_password(user_data["password"])
        
        # Initialize empty arrays if not provided
        user_data.setdefault("skills", [])
        user_data.setdefault("experience", [])
        user_data.setdefault("education", [])
        user_data.setdefault("applications", [])
        
        # Add timestamps
        cls._add_timestamps(user_data)
        
        return insert_one(cls.COLLECTION, user_data)
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        if not email:
            return None
        return find_one(cls.COLLECTION, {"email": email.lower().strip()})
    
    @classmethod
    def update(cls, user_id, user_data):
        """Update user"""
        # Remove password from regular updates
        if "password" in user_data:
            del user_data["password"]
        
        # Validate email if provided
        if "email" in user_data:
            user_data["email"] = cls._validate_email(user_data["email"])
            
            # Check if email is already taken by another user
            existing = cls.find_by_email(user_data["email"])
            if existing and str(existing["_id"]) != str(user_id):
                raise ValidationError("Email already exists")
        
        # Add update timestamp
        cls._add_timestamps(user_data, is_update=True)
        
        return update_one(cls.COLLECTION, user_id, user_data)
    
    @classmethod
    def update_password(cls, user_id, new_password):
        """Update user password"""
        if not new_password:
            raise ValidationError("Password cannot be empty")
        
        hashed_password = hash_password(new_password)
        data = {"password": hashed_password}
        cls._add_timestamps(data, is_update=True)
        
        return update_one(cls.COLLECTION, user_id, data)
    
    @classmethod
    def authenticate(cls, email, password):
        """Authenticate user"""
        if not email or not password:
            return None
        
        user = cls.find_by_email(email)
        if not user or "password" not in user:
            return None
        
        if verify_password(password, user["password"]):
            return user
        
        return None
    
    @classmethod
    def add_experience(cls, user_id, experience_data):
        """Add experience to user"""
        user = cls.find_by_id(user_id)
        if not user:
            raise ValidationError("User not found")
        
        # Validate required fields
        if not experience_data.get("title"):
            raise ValidationError("Experience title is required")
        if not experience_data.get("company"):
            raise ValidationError("Company name is required")
        
        # Generate ID and timestamps
        experience_data["id"] = str(ObjectId())
        cls._add_timestamps(experience_data)
        
        experiences = user.get("experience", [])
        experiences.append(experience_data)
        
        update_data = {"experience": experiences}
        cls._add_timestamps(update_data, is_update=True)
        
        update_one(cls.COLLECTION, user_id, update_data)
        return experience_data["id"]
    
    @classmethod
    def add_education(cls, user_id, education_data):
        """Add education to user"""
        user = cls.find_by_id(user_id)
        if not user:
            raise ValidationError("User not found")
        
        # Validate required fields
        if not education_data.get("school"):
            raise ValidationError("School name is required")
        if not education_data.get("degree"):
            raise ValidationError("Degree is required")
        
        # Generate ID and timestamps
        education_data["id"] = str(ObjectId())
        cls._add_timestamps(education_data)
        
        education = user.get("education", [])
        education.append(education_data)
        
        update_data = {"education": education}
        cls._add_timestamps(update_data, is_update=True)
        
        update_one(cls.COLLECTION, user_id, update_data)
        return education_data["id"]
