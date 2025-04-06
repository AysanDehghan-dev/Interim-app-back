from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from marshmallow import ValidationError

from app.models.application import Application
from app.models.user import User
from app.schemas.application_schema import ApplicationSchema
from app.schemas.user_schema import UserSchema

users_bp = Blueprint("users", __name__)


@users_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Get the authenticated user's profile"""
    try:
        # Check if the authenticated user is a regular user
        claims = get_jwt()
        user_type = claims.get("user_type", "")

        if user_type != "user":
            return jsonify({"error": "Access denied"}), 403

        # Get the authenticated user ID
        user_id = get_jwt_identity()

        # Get the user
        user = User.find_by_id(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify(UserSchema().dump(user)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update the authenticated user's profile"""
    try:
        # Check if the authenticated user is a regular user
        claims = get_jwt()
        user_type = claims.get("user_type", "")

        if user_type != "user":
            return jsonify({"error": "Access denied"}), 403

        # Get the authenticated user ID
        user_id = get_jwt_identity()

        # Validate and deserialize input
        data = UserSchema(partial=True).load(request.json)

        # Don't allow updating email or password through this endpoint
        if "email" in data:
            del data["email"]
        if "password" in data:
            del data["password"]

        # Update user
        User.update(user_id, data)

        # Get the updated user
        updated_user = User.find_by_id(user_id)

        return jsonify(UserSchema().dump(updated_user)), 200

    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/applications", methods=["GET"])
@jwt_required()
def get_applications():
    """Get the authenticated user's job applications"""
    try:
        # Check if the authenticated user is a regular user
        claims = get_jwt()
        user_type = claims.get("user_type", "")

        if user_type != "user":
            return jsonify({"error": "Access denied"}), 403

        # Get the authenticated user ID
        user_id = get_jwt_identity()

        # Get applications for this user
        applications = Application.find_by_user(user_id)

        # Get job data for each application
        from app.models.company import Company
        from app.models.job import Job

        for app in applications:
            job = Job.find_by_id(app["job_id"])
            if job:
                # Get company data
                company = Company.find_by_id(job["company_id"])
                if company:
                    # Remove password field for security
                    if "password" in company:
                        del company["password"]
                    job["company"] = company

                app["job"] = job

        return jsonify(ApplicationSchema(many=True).dump(applications)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/experience", methods=["POST"])
@jwt_required()
def add_experience():
    """Add experience to user profile"""
    try:
        # Check if the authenticated user is a regular user
        claims = get_jwt()
        user_type = claims.get("user_type", "")

        if user_type != "user":
            return jsonify({"error": "Access denied"}), 403

        # Get the authenticated user ID
        user_id = get_jwt_identity()

        # Get experience data from request
        experience_data = request.json

        # Add experience to user
        experience_id = User.add_experience(user_id, experience_data)

        if not experience_id:
            return jsonify({"error": "Failed to add experience"}), 400

        # Get the updated user
        updated_user = User.find_by_id(user_id)

        return jsonify(UserSchema().dump(updated_user)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/education", methods=["POST"])
@jwt_required()
def add_education():
    """Add education to user profile"""
    try:
        # Check if the authenticated user is a regular user
        claims = get_jwt()
        user_type = claims.get("user_type", "")

        if user_type != "user":
            return jsonify({"error": "Access denied"}), 403

        # Get the authenticated user ID
        user_id = get_jwt_identity()

        # Get education data from request
        education_data = request.json

        # Add education to user
        education_id = User.add_education(user_id, education_data)

        if not education_id:
            return jsonify({"error": "Failed to add education"}), 400

        # Get the updated user
        updated_user = User.find_by_id(user_id)

        return jsonify(UserSchema().dump(updated_user)), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
