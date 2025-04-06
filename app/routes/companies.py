from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from marshmallow import ValidationError

from app.models.company import Company
from app.models.job import Job
from app.schemas.company_schema import CompanySchema
from app.schemas.job_schema import JobSchema

companies_bp = Blueprint("companies", __name__)


@companies_bp.route("", methods=["GET"])
def get_companies():
    """Get list of companies"""
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


@companies_bp.route("/<company_id>", methods=["GET"])
def get_company(company_id):
    """Get company details by ID"""
    try:
        company = Company.find_by_id(company_id)

        if not company:
            return jsonify({"error": "Company not found"}), 404

        return jsonify(CompanySchema().dump(company)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@companies_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Get the authenticated company's profile"""
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


@companies_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update the authenticated company's profile"""
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


@companies_bp.route("/jobs", methods=["GET"])
@jwt_required()
def get_company_jobs():
    """Get jobs posted by the authenticated company"""
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


@companies_bp.route("/<company_id>/jobs", methods=["GET"])
def get_jobs_by_company(company_id):
    """Get jobs posted by a specific company"""
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
