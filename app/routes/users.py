from flask import Blueprint, request
from app.models.application import Application
from app.models.user import User
from app.schemas.user import UserSchema, UserUpdateSchema, ExperienceSchema, EducationSchema
from app.schemas.application import ApplicationSchema
from app.utils.decorators import handle_errors, require_user_type, validate_pagination, validate_json
from app.utils.response_helpers import success_response, paginated_response, sanitize_response_data
from app.utils.route_helpers import populate_application_data
from app.utils.db import ensure_document_exists

users_bp = Blueprint("users", __name__)


@users_bp.route("/profile", methods=["GET"])
@handle_errors
@require_user_type("user")
def get_profile(current_user_id, current_user_type):
    """Get the authenticated user's profile"""
    user = ensure_document_exists("users", current_user_id)
    
    return success_response(UserSchema().dump(sanitize_response_data(user)))


@users_bp.route("/profile", methods=["PUT"])
@handle_errors
@require_user_type("user")
@validate_json(UserUpdateSchema)
def update_profile(current_user_id, current_user_type, validated_data):
    """Update the authenticated user's profile"""
    # Update user
    User.update(current_user_id, validated_data)
    
    # Get the updated user
    updated_user = ensure_document_exists("users", current_user_id)
    
    return success_response(
        UserSchema().dump(sanitize_response_data(updated_user)),
        message="Profile updated successfully"
    )


@users_bp.route("/applications", methods=["GET"])
@handle_errors
@require_user_type("user")
@validate_pagination
def get_applications(current_user_id, current_user_type, pagination):
    """Get the authenticated user's job applications"""
    # Get applications for this user
    applications = Application.find_by_user(current_user_id, limit=pagination['limit'], skip=pagination['skip'])
    total = Application.count_all({"user_id": current_user_id})
    
    # Populate application data
    populated_applications = [populate_application_data(app) for app in applications]
    
    return paginated_response(
        ApplicationSchema(many=True).dump(populated_applications),
        total,
        pagination['page'],
        pagination['limit']
    )


@users_bp.route("/experience", methods=["POST"])
@handle_errors
@require_user_type("user")
@validate_json(ExperienceSchema)
def add_experience(current_user_id, current_user_type, validated_data):
    """Add experience to user profile"""
    # Add experience to user
    experience_id = User.add_experience(current_user_id, validated_data)
    
    # Get the updated user
    updated_user = ensure_document_exists("users", current_user_id)
    
    return success_response(
        UserSchema().dump(sanitize_response_data(updated_user)),
        message="Experience added successfully"
    )


@users_bp.route("/education", methods=["POST"])
@handle_errors
@require_user_type("user")
@validate_json(EducationSchema)
def add_education(current_user_id, current_user_type, validated_data):
    """Add education to user profile"""
    # Add education to user
    education_id = User.add_education(current_user_id, validated_data)
    
    # Get the updated user
    updated_user = ensure_document_exists("users", current_user_id)
    
    return success_response(
        UserSchema().dump(sanitize_response_data(updated_user)),
        message="Education added successfully"
    )
