from flask import Blueprint
from app.models.application import Application
from app.schemas.application import ApplicationStatusUpdateSchema, ApplicationSchema
from app.utils.decorators import handle_errors, require_user_type, validate_json
from app.utils.response_helpers import success_response, error_response
from app.utils.route_helpers import populate_application_data, check_resource_ownership
from app.utils.db import ensure_document_exists
from app.models.job import Job

applications_bp = Blueprint("applications", __name__)


@applications_bp.route("/<application_id>/status", methods=["PUT"])
@handle_errors
@require_user_type("company")
@validate_json(ApplicationStatusUpdateSchema)
def update_application_status(application_id, current_user_id, current_user_type, validated_data):
    """Update application status (company only)"""
    # Get the application
    application = ensure_document_exists("applications", application_id)
    
    # Get the job to verify company ownership
    job = ensure_document_exists("jobs", application["job_id"])
    
    if not check_resource_ownership(job, current_user_id, "company_id"):
        return error_response("You do not have permission to update this application", 403, "permission_denied")
    
    # Update application status
    success = Application.update_status(application_id, validated_data["status"])
    
    if not success:
        return error_response("Failed to update application status", 500, "update_failed")
    
    # Get the updated application
    updated_application = ensure_document_exists("applications", application_id)
    updated_application = populate_application_data(updated_application)
    
    return success_response(
        ApplicationSchema().dump(updated_application),
        message="Application status updated successfully"
    )


@applications_bp.route("/<application_id>", methods=["GET"])
@handle_errors
@require_user_type("user")
def get_application(application_id, current_user_id, current_user_type):
    """Get application details (user only, must own the application)"""
    # Get the application
    application = ensure_document_exists("applications", application_id)
    
    # Verify ownership
    if not check_resource_ownership(application, current_user_id, "user_id"):
        return error_response("You do not have permission to view this application", 403, "permission_denied")
    
    # Populate application data
    application = populate_application_data(application)
    
    return success_response(ApplicationSchema().dump(application))