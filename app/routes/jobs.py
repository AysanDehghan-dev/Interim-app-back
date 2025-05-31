from flask import Blueprint, request
from app.models.application import Application
from app.models.company import Company
from app.models.job import Job
from app.schemas.job import JobSchema, JobCreateSchema, JobUpdateSchema, JobSearchSchema
from app.schemas.application import ApplicationSchema, ApplicationCreateSchema
from app.utils.decorators import handle_errors, require_user_type, validate_pagination, validate_json
from app.utils.response_helpers import success_response, paginated_response, error_response
from app.utils.route_helpers import populate_job_data, populate_application_data, check_resource_ownership
from app.utils.db import ensure_document_exists

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("", methods=["GET"])
@handle_errors
@validate_pagination
def search_jobs(pagination):
    """Search jobs with filters"""
    # Parse and validate search parameters
    schema = JobSearchSchema()
    filters = schema.load(request.args)
    
    # Extract pagination from filters if present
    page = filters.pop("page", pagination['page'])
    limit = filters.pop("limit", pagination['limit'])
    skip = filters.pop("skip", pagination['skip'])
    
    # Search jobs
    jobs = Job.search(filters, limit=limit, skip=skip)
    total = Job.count(filters)
    
    # Populate job data with company info
    populated_jobs = [populate_job_data(job) for job in jobs]
    
    return paginated_response(
        JobSchema(many=True).dump(populated_jobs),
        total,
        page,
        limit
    )


@jobs_bp.route("/<job_id>", methods=["GET"])
@handle_errors
def get_job(job_id):
    """Get job details by ID"""
    job = ensure_document_exists("jobs", job_id)
    
    # Populate with company data
    job = populate_job_data(job)
    
    return success_response(JobSchema().dump(job))


@jobs_bp.route("", methods=["POST"])
@handle_errors
@require_user_type("company")
@validate_json(JobCreateSchema)
def create_job(current_user_id, current_user_type, validated_data):
    """Create a new job (company only)"""
    # Set company_id to authenticated company
    validated_data["company_id"] = current_user_id
    
    # Create new job
    job_id = Job.create(validated_data)
    
    # Add job reference to company
    Company.add_job(current_user_id, job_id)
    
    # Get the created job
    job = ensure_document_exists("jobs", job_id)
    job = populate_job_data(job)
    
    return success_response(
        JobSchema().dump(job),
        201,
        "Job created successfully"
    )


@jobs_bp.route("/<job_id>", methods=["PUT"])
@handle_errors
@require_user_type("company")
@validate_json(JobUpdateSchema)
def update_job(job_id, current_user_id, current_user_type, validated_data):
    """Update a job (company only)"""
    # Get the job and verify ownership
    job = ensure_document_exists("jobs", job_id)
    
    if not check_resource_ownership(job, current_user_id, "company_id"):
        return error_response("You do not have permission to update this job", 403, "permission_denied")
    
    # Update job
    Job.update(job_id, validated_data)
    
    # Get the updated job
    updated_job = ensure_document_exists("jobs", job_id)
    updated_job = populate_job_data(updated_job)
    
    return success_response(
        JobSchema().dump(updated_job),
        message="Job updated successfully"
    )


@jobs_bp.route("/<job_id>/apply", methods=["POST"])
@handle_errors
@require_user_type("user")
@validate_json(ApplicationCreateSchema)
def apply_for_job(job_id, current_user_id, current_user_type, validated_data):
    """Apply for a job (user only)"""
    # Verify job exists
    job = ensure_document_exists("jobs", job_id)
    
    # Set job_id and user_id
    validated_data["job_id"] = job_id
    validated_data["user_id"] = current_user_id
    
    # Create application (model will check for duplicates)
    application_id = Application.create(validated_data)
    
    # Add application reference to job
    Job.add_application(job_id, application_id)
    
    # Get the created application
    application = ensure_document_exists("applications", application_id)
    application = populate_application_data(application)
    
    return success_response(
        ApplicationSchema().dump(application),
        201,
        "Application submitted successfully"
    )


@jobs_bp.route("/<job_id>/applications", methods=["GET"])
@handle_errors
@require_user_type("company")
@validate_pagination
def get_job_applications(job_id, current_user_id, current_user_type, pagination):
    """Get applications for a specific job (company only)"""
    # Get the job and verify ownership
    job = ensure_document_exists("jobs", job_id)
    
    if not check_resource_ownership(job, current_user_id, "company_id"):
        return error_response("You do not have permission to view this job's applications", 403, "permission_denied")
    
    # Get applications for this job
    applications = Application.find_by_job(job_id, limit=pagination['limit'], skip=pagination['skip'])
    total = Application.count_all({"job_id": job_id})
    
    # Populate application data
    populated_applications = [populate_application_data(app) for app in applications]
    
    return paginated_response(
        ApplicationSchema(many=True).dump(populated_applications),
        total,
        pagination['page'],
        pagination['limit']
    )