from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from marshmallow import ValidationError

from app.models.company import Company
from app.models.job import Job
from app.schemas.company_schema import CompanySchema
from app.schemas.job_schema import JobSchema

companies_bp = Blueprint("companies", __name__)

# Create namespace for swagger documentation
companies_ns = Namespace("companies", description="Company operations")

# Define models for swagger documentation
company_profile_update_model = companies_ns.model(
    "CompanyProfileUpdate",
    {
        "name": fields.String(description="Company name", example="TechCorp"),
        "industry": fields.String(description="Industry", example="Technology"),
        "description": fields.String(
            description="Company description", example="Leading tech company"
        ),
        "website": fields.String(
            description="Website URL", example="https://techcorp.com"
        ),
        "phone": fields.String(description="Phone number", example="+33 1 23 45 67 89"),
        "address": fields.String(description="Address", example="50 Rue de Innovation"),
        "city": fields.String(description="City", example="Lyon"),
        "country": fields.String(description="Country", example="France"),
        "logo": fields.String(
            description="Logo URL", example="https://techcorp.com/logo.png"
        ),
    },
)

pagination_model = companies_ns.model(
    "Pagination",
    {
        "total": fields.Integer(description="Total number of items"),
        "page": fields.Integer(description="Current page"),
        "limit": fields.Integer(description="Items per page"),
        "pages": fields.Integer(description="Total pages"),
    },
)

companies_response_model = companies_ns.model(
    "CompaniesResponse",
    {
        "companies": fields.List(fields.Raw, description="List of companies"),
        "pagination": fields.Nested(pagination_model),
    },
)

error_model = companies_ns.model(
    "Error",
    {
        "error": fields.String(description="Error type"),
        "message": fields.String(description="Error message"),
    },
)


@companies_ns.route("")
class CompaniesList(Resource):
    @companies_ns.doc("get_companies")
    @companies_ns.param("page", "Page number (default: 1)")
    @companies_ns.param("limit", "Items per page (default: 10)")
    @companies_ns.response(200, "Success", companies_response_model)
    def get(self):
        """Get list of all companies (public endpoint)"""
        try:
            # Get pagination parameters
            page = int(request.args.get("page", 1))
            limit = int(request.args.get("limit", 10))
            skip = (page - 1) * limit

            # Get companies
            companies = Company.find_all(limit=limit, skip=skip)

            # For now, we'll create a simple response since find_all doesn't return total count
            result = {
                "companies": CompanySchema(many=True).dump(companies),
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(
                        companies
                    ),  # This is not accurate for the total, just current page
                    "pages": 1,  # We'd need to modify Company.find_all to get accurate pagination
                },
            }

            return result, 200

        except Exception as e:
            return {"error": str(e)}, 500


@companies_ns.route("/<string:company_id>")
@companies_ns.param("company_id", "Company ID")
class CompanyDetail(Resource):
    @companies_ns.doc("get_company")
    @companies_ns.response(200, "Success - Company details")
    @companies_ns.response(404, "Company not found", error_model)
    def get(self, company_id):
        """Get company details by ID (public endpoint)"""
        try:
            company = Company.find_by_id(company_id)

            if not company:
                return {"error": "Company not found"}, 404

            return CompanySchema().dump(company), 200

        except Exception as e:
            return {"error": str(e)}, 500


@companies_ns.route("/profile")
class CompanyProfile(Resource):
    @companies_ns.doc("get_company_profile", security="Bearer")
    @companies_ns.response(200, "Success - Company profile data")
    @companies_ns.response(401, "Authentication required", error_model)
    @companies_ns.response(403, "Access denied - Companies only", error_model)
    @jwt_required()
    def get(self):
        """Get the authenticated company's profile"""
        try:
            # Check if the authenticated user is a company
            claims = get_jwt()
            user_type = claims.get("user_type", "")

            if user_type != "company":
                return {"error": "Access denied"}, 403

            # Get the authenticated company ID
            company_id = get_jwt_identity()

            # Get the company
            company = Company.find_by_id(company_id)

            if not company:
                return {"error": "Company not found"}, 404

            return CompanySchema().dump(company), 200

        except Exception as e:
            return {"error": str(e)}, 500

    @companies_ns.expect(company_profile_update_model)
    @companies_ns.doc("update_company_profile", security="Bearer")
    @companies_ns.response(200, "Profile updated successfully")
    @companies_ns.response(400, "Validation error", error_model)
    @companies_ns.response(401, "Authentication required", error_model)
    @companies_ns.response(403, "Access denied - Companies only", error_model)
    @jwt_required()
    def put(self):
        """Update the authenticated company's profile"""
        try:
            # Check if the authenticated user is a company
            claims = get_jwt()
            user_type = claims.get("user_type", "")

            if user_type != "company":
                return {"error": "Access denied"}, 403

            # Get the authenticated company ID
            company_id = get_jwt_identity()

            # Validate and deserialize input
            data = CompanySchema(partial=True).load(request.json)

            # Don't allow updating email or password through this endpoint
            if "email" in data:
                del data["email"]
            if "password" in data:
                del data["password"]

            # Update company
            Company.update(company_id, data)

            # Get the updated company
            updated_company = Company.find_by_id(company_id)

            return CompanySchema().dump(updated_company), 200

        except ValidationError as err:
            return {"error": "Validation error", "messages": err.messages}, 400
        except Exception as e:
            return {"error": str(e)}, 500


@companies_ns.route("/jobs")
class CompanyJobs(Resource):
    @companies_ns.doc("get_company_jobs", security="Bearer")
    @companies_ns.response(200, "Success - List of company jobs")
    @companies_ns.response(401, "Authentication required", error_model)
    @companies_ns.response(403, "Access denied - Companies only", error_model)
    @jwt_required()
    def get(self):
        """Get jobs posted by the authenticated company"""
        try:
            # Check if the authenticated user is a company
            claims = get_jwt()
            user_type = claims.get("user_type", "")

            if user_type != "company":
                return {"error": "Access denied"}, 403

            # Get the authenticated company ID
            company_id = get_jwt_identity()

            # Get jobs for this company
            jobs = Job.find_by_company(company_id)

            return JobSchema(many=True).dump(jobs), 200

        except Exception as e:
            return {"error": str(e)}, 500


@companies_ns.route("/<string:company_id>/jobs")
@companies_ns.param("company_id", "Company ID")
class CompanyJobsList(Resource):
    @companies_ns.doc("get_company_jobs_public")
    @companies_ns.response(200, "Success - List of jobs for this company")
    @companies_ns.response(404, "Company not found", error_model)
    def get(self, company_id):
        """Get jobs posted by a specific company (public endpoint)"""
        try:
            # Verify company exists
            company = Company.find_by_id(company_id)

            if not company:
                return {"error": "Company not found"}, 404

            # Get jobs for this company
            jobs = Job.find_by_company(company_id)

            return JobSchema(many=True).dump(jobs), 200

        except Exception as e:
            return {"error": str(e)}, 500


# Keep the original Flask routes for backward compatibility
@companies_bp.route("", methods=["GET"])
def get_companies():
    """Get list of companies"""
    return CompaniesList().get()


@companies_bp.route("/<company_id>", methods=["GET"])
def get_company(company_id):
    """Get company details by ID"""
    return CompanyDetail().get(company_id)


@companies_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Get the authenticated company's profile"""
    return CompanyProfile().get()


@companies_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update the authenticated company's profile"""
    return CompanyProfile().put()


@companies_bp.route("/jobs", methods=["GET"])
@jwt_required()
def get_company_jobs():
    """Get jobs posted by the authenticated company"""
    return CompanyJobs().get()


@companies_bp.route("/<company_id>/jobs", methods=["GET"])
def get_jobs_by_company(company_id):
    """Get jobs posted by a specific company"""
    return CompanyJobsList().get(company_id)
