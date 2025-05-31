from flask import Blueprint, request

from app.models.company import Company
from app.models.job import Job
from app.schemas.company import CompanySchema, CompanyUpdateSchema
from app.schemas.job import JobSchema
from app.utils.db import ensure_document_exists
from app.utils.decorators import (
    handle_errors,
    require_user_type,
    validate_json,
    validate_pagination,
)
from app.utils.response_helpers import (
    paginated_response,
    sanitize_response_data,
    success_response,
)
from app.utils.route_helpers import populate_job_data

companies_bp = Blueprint("companies", __name__)


@companies_bp.route("", methods=["GET"])
@handle_errors
@validate_pagination
def get_companies(pagination):
    """Get list of companies"""
    # Get companies
    companies = Company.find_all(limit=pagination["limit"], skip=pagination["skip"])
    total = Company.count_all()

    # Sanitize response data
    sanitized_companies = sanitize_response_data(companies)

    return paginated_response(
        CompanySchema(many=True).dump(sanitized_companies),
        total,
        pagination["page"],
        pagination["limit"],
    )


@companies_bp.route("/<company_id>", methods=["GET"])
@handle_errors
def get_company(company_id):
    """Get company details by ID"""
    company = ensure_document_exists("companies", company_id)

    return success_response(CompanySchema().dump(sanitize_response_data(company)))


@companies_bp.route("/profile", methods=["GET"])
@handle_errors
@require_user_type("company")
def get_profile(current_user_id, current_user_type):
    """Get the authenticated company's profile"""
    company = ensure_document_exists("companies", current_user_id)

    return success_response(CompanySchema().dump(sanitize_response_data(company)))


@companies_bp.route("/profile", methods=["PUT"])
@handle_errors
@require_user_type("company")
@validate_json(CompanyUpdateSchema)
def update_profile(current_user_id, current_user_type, validated_data):
    """Update the authenticated company's profile"""
    # Update company
    Company.update(current_user_id, validated_data)

    # Get the updated company
    updated_company = ensure_document_exists("companies", current_user_id)

    return success_response(
        CompanySchema().dump(sanitize_response_data(updated_company)),
        message="Profile updated successfully",
    )


@companies_bp.route("/jobs", methods=["GET"])
@handle_errors
@require_user_type("company")
@validate_pagination
def get_company_jobs(current_user_id, current_user_type, pagination):
    """Get jobs posted by the authenticated company"""
    # Get jobs for this company
    jobs = Job.find_by_company(
        current_user_id, limit=pagination["limit"], skip=pagination["skip"]
    )
    total = Job.count({"company_id": current_user_id})

    return paginated_response(
        JobSchema(many=True).dump(jobs), total, pagination["page"], pagination["limit"]
    )


@companies_bp.route("/<company_id>/jobs", methods=["GET"])
@handle_errors
@validate_pagination
def get_jobs_by_company(company_id, pagination):
    """Get jobs posted by a specific company"""
    # Verify company exists
    ensure_document_exists("companies", company_id)

    # Get jobs for this company
    jobs = Job.find_by_company(
        company_id, limit=pagination["limit"], skip=pagination["skip"]
    )
    total = Job.count({"company_id": company_id})

    return paginated_response(
        JobSchema(many=True).dump(jobs), total, pagination["page"], pagination["limit"]
    )
