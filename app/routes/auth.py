from flask import Blueprint, request
from app.models.company import Company
from app.models.user import User
from app.schemas.company import CompanyLoginSchema, CompanyRegisterSchema, CompanySchema
from app.schemas.user import UserLoginSchema, UserRegisterSchema, UserSchema
from app.utils.security import generate_tokens, sanitize_user_data
from app.utils.decorators import handle_errors, validate_json
from app.utils.response_helpers import success_response, error_response

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register/user", methods=["POST"])
@handle_errors
@validate_json(UserRegisterSchema)
def register_user(validated_data):
    """Register a new user"""
    # Create new user
    user_id = User.create(validated_data)
    
    # Get the created user
    user = User.find_by_id(user_id)
    
    # Generate authentication tokens
    tokens = generate_tokens(user_id, "user")
    
    # Prepare response
    response_data = {
        "user": UserSchema().dump(sanitize_user_data(user)),
        **tokens
    }
    
    return success_response(response_data, 201, "User registered successfully")


@auth_bp.route("/register/company", methods=["POST"])
@handle_errors
@validate_json(CompanyRegisterSchema)
def register_company(validated_data):
    """Register a new company"""
    # Create new company
    company_id = Company.create(validated_data)
    
    # Get the created company
    company = Company.find_by_id(company_id)
    
    # Generate authentication tokens
    tokens = generate_tokens(company_id, "company")
    
    # Prepare response
    response_data = {
        "company": CompanySchema().dump(sanitize_user_data(company)),
        **tokens
    }
    
    return success_response(response_data, 201, "Company registered successfully")


@auth_bp.route("/login/user", methods=["POST"])
@handle_errors
@validate_json(UserLoginSchema)
def login_user(validated_data):
    """Login for users"""
    # Authenticate user
    user = User.authenticate(validated_data["email"], validated_data["password"])
    if not user:
        return error_response("Invalid email or password", 401, "authentication_failed")
    
    # Generate authentication tokens
    tokens = generate_tokens(user["_id"], "user")
    
    # Prepare response
    response_data = {
        "user": UserSchema().dump(sanitize_user_data(user)),
        **tokens
    }
    
    return success_response(response_data, message="Login successful")


@auth_bp.route("/login/company", methods=["POST"])
@handle_errors
@validate_json(CompanyLoginSchema)
def login_company(validated_data):
    """Login for companies"""
    # Authenticate company
    company = Company.authenticate(validated_data["email"], validated_data["password"])
    if not company:
        return error_response("Invalid email or password", 401, "authentication_failed")
    
    # Generate authentication tokens
    tokens = generate_tokens(company["_id"], "company")
    
    # Prepare response
    response_data = {
        "company": CompanySchema().dump(sanitize_user_data(company)),
        **tokens
    }
    
    return success_response(response_data, message="Login successful")
