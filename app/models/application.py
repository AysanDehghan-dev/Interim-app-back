from app.utils.db import insert_one, find_one, update_one, find_by_id, find_many
from bson.objectid import ObjectId
from datetime import datetime

class ApplicationStatus:
    """Application status enumeration"""
    PENDING = 'PENDING'
    REVIEWING = 'REVIEWING'
    INTERVIEW = 'INTERVIEW'
    REJECTED = 'REJECTED'
    ACCEPTED = 'ACCEPTED'

class Application:
    """Application model class"""
    
    COLLECTION = 'applications'
    
    @staticmethod
    def create(application_data):
        """
        Create a new application
        """
        # Make sure job_id and user_id are stored as ObjectId
        if 'job_id' in application_data and not isinstance(application_data['job_id'], ObjectId):
            application_data['job_id'] = ObjectId(application_data['job_id'])
        
        if 'user_id' in application_data and not isinstance(application_data['user_id'], ObjectId):
            application_data['user_id'] = ObjectId(application_data['user_id'])
        
        # Set default status if not provided
        if 'status' not in application_data:
            application_data['status'] = ApplicationStatus.PENDING
        
        # Add timestamps if not provided
        if 'created_at' not in application_data:
            application_data['created_at'] = datetime.utcnow()
        if 'updated_at' not in application_data:
            application_data['updated_at'] = datetime.utcnow()
        
        application_id = insert_one(Application.COLLECTION, application_data)
        return application_id
    
    @staticmethod
    def find_by_id(application_id):
        """
        Find an application by ID
        """
        return find_by_id(Application.COLLECTION, application_id)
    
    @staticmethod
    def find_by_user(user_id, limit=0, skip=0):
        """
        Find applications by user ID
        """
        query = {"user_id": ObjectId(user_id)}
        return find_many(Application.COLLECTION, query, limit=limit, skip=skip)
    
    @staticmethod
    def find_by_job(job_id, limit=0, skip=0):
        """
        Find applications by job ID
        """
        query = {"job_id": ObjectId(job_id)}
        return find_many(Application.COLLECTION, query, limit=limit, skip=skip)
    
    @staticmethod
    def find_by_user_and_job(user_id, job_id):
        """
        Find an application by user ID and job ID
        """
        query = {
            "user_id": ObjectId(user_id),
            "job_id": ObjectId(job_id)
        }
        return find_one(Application.COLLECTION, query)
    
    @staticmethod
    def update_status(application_id, status):
        """
        Update application status
        """
        # Validate status
        valid_statuses = [
            ApplicationStatus.PENDING,
            ApplicationStatus.REVIEWING,
            ApplicationStatus.INTERVIEW,
            ApplicationStatus.REJECTED,
            ApplicationStatus.ACCEPTED
        ]
        
        if status not in valid_statuses:
            return False
        
        # Update the status and updated_at timestamp
        updates = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        result = update_one(Application.COLLECTION, application_id, updates)
        return result > 0