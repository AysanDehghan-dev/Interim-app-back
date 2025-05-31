from app.utils.db import find_one, find_many, insert_one, update_one
from app.models.base import BaseModel
from app.models.exceptions import ValidationError
from app.models.enums import ApplicationStatus


class Application(BaseModel):
    """Application model class"""
    
    COLLECTION = "applications"
    
    @classmethod
    def create(cls, application_data):
        """Create a new application"""
        # Validate required fields
        if not application_data.get("job_id"):
            raise ValidationError("Job ID is required")
        if not application_data.get("user_id"):
            raise ValidationError("User ID is required")
        
        # Validate ObjectIds
        application_data["job_id"] = cls._validate_object_id(application_data["job_id"], "job_id")
        application_data["user_id"] = cls._validate_object_id(application_data["user_id"], "user_id")
        
        # Check if user already applied for this job
        existing = cls.find_by_user_and_job(
            application_data["user_id"], 
            application_data["job_id"]
        )
        if existing:
            raise ValidationError("User has already applied for this job")
        
        # Set default status
        application_data.setdefault("status", ApplicationStatus.PENDING)
        
        # Validate status
        if not ApplicationStatus.is_valid(application_data["status"]):
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(ApplicationStatus.get_all())}")
        
        # Add timestamps
        cls._add_timestamps(application_data)
        
        return insert_one(cls.COLLECTION, application_data)
    
    @classmethod
    def find_by_user(cls, user_id, limit=0, skip=0):
        """Find applications by user"""
        user_id = cls._validate_object_id(user_id, "user_id")
        query = {"user_id": user_id}
        sort = [("created_at", -1)]
        
        return find_many(cls.COLLECTION, query, sort=sort, limit=limit, skip=skip)
    
    @classmethod
    def find_by_job(cls, job_id, limit=0, skip=0):
        """Find applications by job"""
        job_id = cls._validate_object_id(job_id, "job_id")
        query = {"job_id": job_id}
        sort = [("created_at", -1)]
        
        return find_many(cls.COLLECTION, query, sort=sort, limit=limit, skip=skip)
    
    @classmethod
    def find_by_user_and_job(cls, user_id, job_id):
        """Find application by user and job"""
        user_id = cls._validate_object_id(user_id, "user_id")
        job_id = cls._validate_object_id(job_id, "job_id")
        
        query = {"user_id": user_id, "job_id": job_id}
        return find_one(cls.COLLECTION, query)
    
    @classmethod
    def update_status(cls, application_id, status):
        """Update application status"""
        # Validate status
        if not ApplicationStatus.is_valid(status):
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(ApplicationStatus.get_all())}")
        
        # Update status and timestamp
        update_data = {"status": status}
        cls._add_timestamps(update_data, is_update=True)
        
        result = update_one(cls.COLLECTION, application_id, update_data)
        return result > 0
    
    @classmethod
    def get_by_status(cls, status, limit=0, skip=0):
        """Get applications by status"""
        if not ApplicationStatus.is_valid(status):
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(ApplicationStatus.get_all())}")
        
        query = {"status": status}
        sort = [("created_at", -1)]
        
        return find_many(cls.COLLECTION, query, sort=sort, limit=limit, skip=skip)