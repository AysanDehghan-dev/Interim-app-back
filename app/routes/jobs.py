from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from bson import ObjectId
import math

from app.models.job import Job
from app.models.company import Company
from app.models.application import Application
from app.schemas.job_schema import JobSchema, JobSearchSchema
from app.schemas.application_schema import ApplicationSchema

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("", methods=["GET"])
def search_jobs():
    """Search jobs with filters"""
    try:
        # Parse query parameters
        schema = JobSearchSchema()
        filters = schema.load(request.args)

        # Get pagination parameters
        page = filters.pop("page", 1)
        limit = filters.pop("limit", 10)
        skip = (page - 1) * limit

        # Search jobs
        jobs = Job.search(filters, limit=limit, skip=skip)
        total = Job.count(filters)

        # Prepare response with pagination
        total_pages = math.ceil(total / limit)
        result = {
            "jobs": JobSchema(many=True).dump(jobs),
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": total_pages,
            },
        }

        return jsonify(result), 200

    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@jobs_bp.route("/<job_id>", methods=["GET"])
def get_job(job_id):
    """Get job details by ID"""
    try:
        job = Job.find_by_id(job_id)

        if not job:
            return jsonify({"error": "Job not found"}), 404

        # Get company details
        from app.models.company import Company

        company = Company.find_by_id(job["company_id"])
        if company:
            # Remove password field for security
            if "password" in company:
                del company["password"]
            job["company"] = company

        return jsonify(JobSchema().dump(job)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@jobs_bp.route("", methods=["POST"])
@jwt_required()
def create_job():
    """Create a new job (company only)"""
    try:
        # Check if the authenticated user is a company
        claims = get_jwt()
        user_type = claims.get("user_type", "")

        if user_type != "company":
            return jsonify({"error": "Only companies can create job listings"}), 403

        # Get the authenticated company ID
        company_id = get_jwt_identity()

        # Validate and deserialize input
        data = JobSchema().load(request.json)

        # Override company_id with the authenticated company's ID
        data["company_id"] = ObjectId(company_id)

        # Create new job
        job_id = Job.create(data)

        # Add job reference to company
        Company.add_job(company_id, job_id)

        # Get the created job
        job = Job.find_by_id(job_id)

        return jsonify(JobSchema().dump(job)), 201

    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@jobs_bp.route("/<job_id>", methods=["PUT"])
@jwt_required()
def update_job(job_id):
    """Update a job (company only)"""
    try:
        # Check if the authenticated user is a company
        claims = get_jwt()
        user_type = claims.get("user_type", "")

        if user_type != "company":
            return jsonify({"error": "Only companies can update job listings"}), 403

        # Get the authenticated company ID
        company_id = get_jwt_identity()

        # Get the job
        job = Job.find_by_id(job_id)

        if not job:
            return jsonify({"error": "Job not found"}), 404

        # Check if the job belongs to the authenticated company
        if str(job["company_id"]) != company_id:
            return (
                jsonify({"error": "You do not have permission to update this job"}),
                403,
            )

        # Validate and deserialize input
        data = JobSchema(partial=True).load(request.json)

        # Don't allow changing company_id
        if "company_id" in data:
            del data["company_id"]

        # Update job
        Job.update(job_id, data)

        # Get the updated job
        updated_job = Job.find_by_id(job_id)

        return jsonify(JobSchema().dump(updated_job)), 200

    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@jobs_bp.route("/<job_id>/apply", methods=["POST"])
@jwt_required()
def apply_for_job(job_id):
    """Apply for a job (user only)"""
    try:
        # Check if the authenticated user is a regular user
        claims = get_jwt()
        user_type = claims.get("user_type", "")

        if user_type != "user":
            return jsonify({"error": "Only users can apply for jobs"}), 403

        # Get the authenticated user ID
        user_id = get_jwt_identity()

        # Get the job
        job = Job.find_by_id(job_id)

        if not job:
            return jsonify({"error": "Job not found"}), 404

        # Check if user has already applied for this job
        existing_application = Application.find_by_user_and_job(user_id, job_id)
        if existing_application:
            return jsonify({"error": "You have already applied for this job"}), 400

        # Create application data
        application_data = {"job_id": ObjectId(job_id), "user_id": ObjectId(user_id)}

        # Add cover letter if provided
        if "coverLetter" in request.json:
            application_data["cover_letter"] = request.json["coverLetter"]

        # Add resume if provided
        if "resume" in request.json:
            application_data["resume"] = request.json["resume"]

        # Create application
        application_id = Application.create(application_data)

        # Add application reference to job
        Job.add_application(job_id, application_id)

        # Get the created application
        application = Application.find_by_id(application_id)

        return jsonify(ApplicationSchema().dump(application)), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@jobs_bp.route("/<job_id>/applications", methods=["GET"])
@jwt_required()
def get_job_applications(job_id):
    """Get applications for a specific job (company only)"""
    try:
        # Check if the authenticated user is a company
        claims = get_jwt()
        user_type = claims.get("user_type", "")

        if user_type != "company":
            return jsonify({"error": "Only companies can view job applications"}), 403

        # Get the authenticated company ID
        company_id = get_jwt_identity()

        # Get the job
        job = Job.find_by_id(job_id)

        if not job:
            return jsonify({"error": "Job not found"}), 404

        # Check if the job belongs to the authenticated company
        if str(job["company_id"]) != company_id:
            return (
                jsonify(
                    {
                        "error": "You do not have permission to view this job's applications"
                    }
                ),
                403,
            )

        # Get applications for this job
        applications = Application.find_by_job(job_id)

        # Get user data for each application
        from app.models.user import User

        for app in applications:
            user = User.find_by_id(app["user_id"])
            if user:
                # Remove password field for security
                if "password" in user:
                    del user["password"]
                app["user"] = user

        return jsonify(ApplicationSchema(many=True).dump(applications)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
