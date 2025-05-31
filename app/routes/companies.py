<<<<<<< HEAD
from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from marshmallow import ValidationError

||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from marshmallow import ValidationError

=======
from flask import Blueprint, request
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)
from app.models.company import Company
from app.models.job import Job
from app.schemas.company import CompanySchema, CompanyUpdateSchema
from app.schemas.job import JobSchema
from app.utils.decorators import handle_errors, require_user_type, validate_pagination, validate_json
from app.utils.response_helpers import success_response, paginated_response, sanitize_response_data
from app.utils.route_helpers import populate_job_data
from app.utils.db import ensure_document_exists

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
@handle_errors
@validate_pagination
def get_companies(pagination):
    """Get list of companies"""
<<<<<<< HEAD
    return CompaniesList().get()
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
    try:
        # Get pagination parameters
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        skip = (page - 1) * limit

        # Get companies
        companies = Company.find_all(limit=limit, skip=skip)

        return jsonify(CompanySchema(many=True).dump(companies)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
=======
    # Get companies
    companies = Company.find_all(limit=pagination['limit'], skip=pagination['skip'])
    total = Company.count_all()
    
    # Sanitize response data
    sanitized_companies = sanitize_response_data(companies)
    
    return paginated_response(
        CompanySchema(many=True).dump(sanitized_companies),
        total,
        pagination['page'],
        pagination['limit']
    )
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


@companies_bp.route("/<company_id>", methods=["GET"])
@handle_errors
def get_company(company_id):
    """Get company details by ID"""
<<<<<<< HEAD
    return CompanyDetail().get(company_id)
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
    try:
        company = Company.find_by_id(company_id)

        if not company:
            return jsonify({"error": "Company not found"}), 404

        return jsonify(CompanySchema().dump(company)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
=======
    company = ensure_document_exists("companies", company_id)
    
    return success_response(CompanySchema().dump(sanitize_response_data(company)))
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


@companies_bp.route("/profile", methods=["GET"])
@handle_errors
@require_user_type("company")
def get_profile(current_user_id, current_user_type):
    """Get the authenticated company's profile"""
<<<<<<< HEAD
    return CompanyProfile().get()
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
    try:
        # Check if the authenticated user is a company
        claims = get_jwt()
        user_type = claims.get("user_type", "")

        if user_type != "company":
            return jsonify({"error": "Access denied"}), 403

        # Get the authenticated company ID
        company_id = get_jwt_identity()

        # Get the company
        company = Company.find_by_id(company_id)

        if not company:
            return jsonify({"error": "Company not found"}), 404

        return jsonify(CompanySchema().dump(company)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
=======
    company = ensure_document_exists("companies", current_user_id)
    
    return success_response(CompanySchema().dump(sanitize_response_data(company)))
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


@companies_bp.route("/profile", methods=["PUT"])
@handle_errors
@require_user_type("company")
@validate_json(CompanyUpdateSchema)
def update_profile(current_user_id, current_user_type, validated_data):
    """Update the authenticated company's profile"""
<<<<<<< HEAD
    return CompanyProfile().put()
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
    try:
        # Check if the authenticated user is a company
        claims = get_jwt()
        user_type = claims.get("user_type", "")

        if user_type != "company":
            return jsonify({"error": "Access denied"}), 403

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

        return jsonify(CompanySchema().dump(updated_company)), 200

    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
=======
    # Update company
    Company.update(current_user_id, validated_data)
    
    # Get the updated company
    updated_company = ensure_document_exists("companies", current_user_id)
    
    return success_response(
        CompanySchema().dump(sanitize_response_data(updated_company)),
        message="Profile updated successfully"
    )
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


@companies_bp.route("/jobs", methods=["GET"])
@handle_errors
@require_user_type("company")
@validate_pagination
def get_company_jobs(current_user_id, current_user_type, pagination):
    """Get jobs posted by the authenticated company"""
<<<<<<< HEAD
    return CompanyJobs().get()
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
    try:
        # Check if the authenticated user is a company
        claims = get_jwt()
        user_type = claims.get("user_type", "")

        if user_type != "company":
            return jsonify({"error": "Access denied"}), 403

        # Get the authenticated company ID
        company_id = get_jwt_identity()

        # Get jobs for this company
        jobs = Job.find_by_company(company_id)

        return jsonify(JobSchema(many=True).dump(jobs)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
=======
    # Get jobs for this company
    jobs = Job.find_by_company(current_user_id, limit=pagination['limit'], skip=pagination['skip'])
    total = Job.count({"company_id": current_user_id})
    
    return paginated_response(
        JobSchema(many=True).dump(jobs),
        total,
        pagination['page'],
        pagination['limit']
    )
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


@companies_bp.route("/<company_id>/jobs", methods=["GET"])
@handle_errors
@validate_pagination
def get_jobs_by_company(company_id, pagination):
    """Get jobs posted by a specific company"""
<<<<<<< HEAD
    return CompanyJobsList().get(company_id)
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
    try:
        # Verify company exists
        company = Company.find_by_id(company_id)

        if not company:
            return jsonify({"error": "Company not found"}), 404

        # Get jobs for this company
        jobs = Job.find_by_company(company_id)

        return jsonify(JobSchema(many=True).dump(jobs)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
=======
    # Verify company exists
    ensure_document_exists("companies", company_id)
    
    # Get jobs for this company
    jobs = Job.find_by_company(company_id, limit=pagination['limit'], skip=pagination['skip'])
    total = Job.count({"company_id": company_id})
    
    return paginated_response(
        JobSchema(many=True).dump(jobs),
        total,
        pagination['page'],
        pagination['limit']
    )
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)
