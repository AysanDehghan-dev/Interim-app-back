import math

from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_restx import Resource, Namespace, fields
from marshmallow import ValidationError

from app.models.application import Application
from app.models.company import Company
from app.models.job import Job
from app.schemas.application_schema import ApplicationSchema
from app.schemas.job_schema import JobSchema, JobSearchSchema

jobs_bp = Blueprint("jobs", __name__)

# Create namespace for swagger documentation
jobs_ns = Namespace('jobs', description='Job operations')

# Define models for swagger documentation
salary_model = jobs_ns.model('Salary', {
    'min': fields.Integer(required=True, description='Minimum salary', example=40000),
    'max': fields.Integer(required=True, description='Maximum salary', example=55000),
    'currency': fields.String(required=True, description='Currency', example='EUR'),
})

job_create_model = jobs_ns.model('JobCreate', {
    'title': fields.String(required=True, description='Job title', example='Frontend Developer'),
    'description': fields.String(required=True, description='Job description', example='We are looking for a skilled frontend developer...'),
    'requirements': fields.List(fields.String, required=True, description='Job requirements', 
                               example=['3+ years React experience', 'JavaScript/TypeScript', 'HTML/CSS']),
    'location': fields.String(required=True, description='Job location', example='Lyon, France'),
    'type': fields.String(required=True, description='Job type', 
                         enum=['FULL_TIME', 'PART_TIME', 'CONTRACT', 'TEMPORARY', 'INTERNSHIP'],
                         example='FULL_TIME'),
    'salary': fields.Nested(salary_model, description='Salary information'),
})

job_application_model = jobs_ns.model('JobApplication', {
    'coverLetter': fields.String(description='Cover letter', example='I am very interested in this position because...'),
    'resume': fields.String(description='Resume/CV content', example='My resume content...'),
})

pagination_model = jobs_ns.model('Pagination', {
    'total': fields.Integer(description='Total number of items'),
    'page': fields.Integer(description='Current page'),
    'limit': fields.Integer(description='Items per page'),
    'pages': fields.Integer(description='Total pages'),
})

jobs_response_model = jobs_ns.model('JobsResponse', {
    'jobs': fields.List(fields.Raw, description='List of jobs'),
    'pagination': fields.Nested(pagination_model),
})

error_model = jobs_ns.model('Error', {
    'error': fields.String(description='Error type'),
    'message': fields.String(description='Error message'),
})

# Register routes with swagger documentation
@jobs_ns.route('')
class JobsList(Resource):
    @jobs_ns.doc('search_jobs')
    @jobs_ns.param('keyword', 'Search keyword for title/description')
    @jobs_ns.param('location', 'Job location filter')
    @jobs_ns.param('type', 'Job type filter', enum=['FULL_TIME', 'PART_TIME', 'CONTRACT', 'TEMPORARY', 'INTERNSHIP'])
    @jobs_ns.param('page', 'Page number (default: 1)')
    @jobs_ns.param('limit', 'Items per page (default: 10)')
    @jobs_ns.response(200, 'Success', jobs_response_model)
    @jobs_ns.response(400, 'Validation error', error_model)
    def get(self):
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
            total_pages = math.ceil(total / limit) if total > 0 else 1
            result = {
                "jobs": JobSchema(many=True).dump(jobs),
                "pagination": {
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "pages": total_pages,
                },
            }

            return result, 200

        except ValidationError as err:
            return {"error": "Validation error", "messages": err.messages}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    @jobs_ns.expect(job_create_model)
    @jobs_ns.doc('create_job', security='Bearer')
    @jobs_ns.response(201, 'Job created successfully')
    @jobs_ns.response(403, 'Only companies can create jobs', error_model)
    @jobs_ns.response(400, 'Validation error', error_model)
    @jwt_required()
    def post(self):
        """Create a new job (company only)"""
        try:
            # Check if the authenticated user is a company
            claims = get_jwt()
            user_type = claims.get("user_type", "")

            if user_type != "company":
                return {"error": "Only companies can create job listings"}, 403

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

            return JobSchema().dump(job), 201

        except ValidationError as err:
            return {"error": "Validation error", "messages": err.messages}, 400
        except Exception as e:
            return {"error": str(e)}, 500

@jobs_ns.route('/<string:job_id>')
@jobs_ns.param('job_id', 'Job ID')
class JobDetail(Resource):
    @jobs_ns.doc('get_job')
    @jobs_ns.response(200, 'Success')
    @jobs_ns.response(404, 'Job not found', error_model)
    def get(self, job_id):
        """Get job details by ID"""
        try:
            job = Job.find_by_id(job_id)

            if not job:
                return {"error": "Job not found"}, 404

            # Get company details
            company = Company.find_by_id(job["company_id"])
            if company:
                # Remove password field for security
                if "password" in company:
                    del company["password"]
                job["company"] = company

            return JobSchema().dump(job), 200

        except Exception as e:
            return {"error": str(e)}, 500

    @jobs_ns.expect(job_create_model)
    @jobs_ns.doc('update_job', security='Bearer')
    @jobs_ns.response(200, 'Job updated successfully')
    @jobs_ns.response(403, 'Only job owner can update', error_model)
    @jobs_ns.response(404, 'Job not found', error_model)
    @jwt_required()
    def put(self, job_id):
        """Update a job (company only)"""
        try:
            # Check if the authenticated user is a company
            claims = get_jwt()
            user_type = claims.get("user_type", "")

            if user_type != "company":
                return {"error": "Only companies can update job listings"}, 403

            # Get the authenticated company ID
            company_id = get_jwt_identity()

            # Get the job
            job = Job.find_by_id(job_id)

            if not job:
                return {"error": "Job not found"}, 404

            # Check if the job belongs to the authenticated company
            if str(job["company_id"]) != company_id:
                return {"error": "You do not have permission to update this job"}, 403

            # Validate and deserialize input
            data = JobSchema(partial=True).load(request.json)

            # Don't allow changing company_id
            if "company_id" in data:
                del data["company_id"]

            # Update job
            Job.update(job_id, data)

            # Get the updated job
            updated_job = Job.find_by_id(job_id)

            return JobSchema().dump(updated_job), 200

        except ValidationError as err:
            return {"error": "Validation error", "messages": err.messages}, 400
        except Exception as e:
            return {"error": str(e)}, 500

@jobs_ns.route('/<string:job_id>/apply')
@jobs_ns.param('job_id', 'Job ID')
class JobApplication(Resource):
    @jobs_ns.expect(job_application_model)
    @jobs_ns.doc('apply_job', security='Bearer')
    @jobs_ns.response(201, 'Application submitted successfully')
    @jobs_ns.response(400, 'Already applied or validation error', error_model)
    @jobs_ns.response(403, 'Only users can apply', error_model)
    @jobs_ns.response(404, 'Job not found', error_model)
    @jwt_required()
    def post(self, job_id):
        """Apply for a job (user only)"""
        try:
            # Check if the authenticated user is a regular user
            claims = get_jwt()
            user_type = claims.get("user_type", "")

            if user_type != "user":
                return {"error": "Only users can apply for jobs"}, 403

            # Get the authenticated user ID
            user_id = get_jwt_identity()

            # Get the job
            job = Job.find_by_id(job_id)

            if not job:
                return {"error": "Job not found"}, 404

            # Check if user has already applied for this job
            existing_application = Application.find_by_user_and_job(user_id, job_id)
            if existing_application:
                return {"error": "You have already applied for this job"}, 400

            # Create application data
            application_data = {"job_id": ObjectId(job_id), "user_id": ObjectId(user_id)}

            # Add cover letter if provided
            if request.json and "coverLetter" in request.json:
                application_data["cover_letter"] = request.json["coverLetter"]

            # Add resume if provided
            if request.json and "resume" in request.json:
                application_data["resume"] = request.json["resume"]

            # Create application
            application_id = Application.create(application_data)

            # Add application reference to job
            Job.add_application(job_id, application_id)

            # Get the created application
            application = Application.find_by_id(application_id)

            return ApplicationSchema().dump(application), 201

        except Exception as e:
            return {"error": str(e)}, 500

@jobs_ns.route('/<string:job_id>/applications')
@jobs_ns.param('job_id', 'Job ID')
class JobApplicationsList(Resource):
    @jobs_ns.doc('get_job_applications', security='Bearer')
    @jobs_ns.response(200, 'Success')
    @jobs_ns.response(403, 'Only job owner can view applications', error_model)
    @jobs_ns.response(404, 'Job not found', error_model)
    @jwt_required()
    def get(self, job_id):
        """Get applications for a specific job (company only)"""
        try:
            # Check if the authenticated user is a company
            claims = get_jwt()
            user_type = claims.get("user_type", "")

            if user_type != "company":
                return {"error": "Only companies can view job applications"}, 403

            # Get the authenticated company ID
            company_id = get_jwt_identity()

            # Get the job
            job = Job.find_by_id(job_id)

            if not job:
                return {"error": "Job not found"}, 404

            # Check if the job belongs to the authenticated company
            if str(job["company_id"]) != company_id:
                return {"error": "You do not have permission to view this job's applications"}, 403

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

            return ApplicationSchema(many=True).dump(applications), 200

        except Exception as e:
            return {"error": str(e)}, 500

# Keep the original Flask routes for backward compatibility
@jobs_bp.route("", methods=["GET"])
def search_jobs():
    """Search jobs with filters"""
    return JobsList().get()

@jobs_bp.route("/<job_id>", methods=["GET"])
def get_job(job_id):
    """Get job details by ID"""
    return JobDetail().get(job_id)

@jobs_bp.route("", methods=["POST"])
@jwt_required()
def create_job():
    """Create a new job (company only)"""
    return JobsList().post()

@jobs_bp.route("/<job_id>", methods=["PUT"])
@jwt_required()
def update_job(job_id):
    """Update a job (company only)"""
    return JobDetail().put(job_id)

@jobs_bp.route("/<job_id>/apply", methods=["POST"])
@jwt_required()
def apply_for_job(job_id):
    """Apply for a job (user only)"""
    return JobApplication().post(job_id)

@jobs_bp.route("/<job_id>/applications", methods=["GET"])
@jwt_required()
def get_job_applications(job_id):
    """Get applications for a specific job (company only)"""
    return JobApplicationsList().get(job_id)