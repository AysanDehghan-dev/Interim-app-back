from app.models.user import User
from app.models.company import Company
from app.models.job import Job
from app.utils.security import sanitize_user_data


def populate_job_data(job):
    """Add company data to job object"""
    if not job or "company_id" not in job:
        return job
    
    company = Company.find_by_id(job["company_id"])
    if company:
        job["company"] = sanitize_user_data(company)
    
    return job


def populate_application_data(application):
    """Add job and user data to application object"""
    if not application:
        return application
    
    # Add job data
    if "job_id" in application:
        job = Job.find_by_id(application["job_id"])
        if job:
            job = populate_job_data(job)  # Also add company to job
            application["job"] = job
    
    # Add user data
    if "user_id" in application:
        user = User.find_by_id(application["user_id"])
        if user:
            application["user"] = sanitize_user_data(user)
    
    return application


def check_resource_ownership(resource, user_id, owner_field="user_id"):
    """Check if user owns the resource"""
    if not resource:
        return False
    
    return str(resource.get(owner_field)) == str(user_id)
