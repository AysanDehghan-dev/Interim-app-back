from flask import Blueprint, jsonify, request
from flask_restx import Namespace, Resource, fields
from marshmallow import ValidationError

from app.models.company import Company
from app.models.user import User
from app.schemas.company_schema import (
    CompanyLoginSchema,
    CompanyRegisterSchema,
    CompanySchema,
)
from app.schemas.user_schema import UserLoginSchema, UserRegisterSchema, UserSchema
from app.utils.security import generate_token

auth_bp = Blueprint("auth", __name__)

# Create namespace for swagger documentation
auth_ns = Namespace("auth", description="Authentication operations")

# Define models for swagger documentation
user_register_model = auth_ns.model(
    "UserRegister",
    {
        "firstName": fields.String(
            required=True,
            description="User first name",
            example="Marie",
            default="Marie",
        ),
        "lastName": fields.String(
            required=True,
            description="User last name",
            example="Martin",
            default="Martin",
        ),
        "email": fields.String(
            required=True,
            description="User email (must be unique)",
            example="marie.martin@example.com",
            default="marie.martin@example.com",
        ),
        "password": fields.String(
            required=True,
            description="Password (minimum 6 characters)",
            example="mypassword123",
            default="mypassword123",
        ),
        "confirmPassword": fields.String(
            required=True,
            description="Confirm password (must match password)",
            example="mypassword123",
            default="mypassword123",
        ),
        "phone": fields.String(
            description="Phone number",
            example="+33 6 98 76 54 32",
            default="+33 6 98 76 54 32",
        ),
        "address": fields.String(
            description="Home address",
            example="123 Rue de la Paix",
            default="123 Rue de la Paix",
        ),
        "city": fields.String(description="City", example="Paris", default="Paris"),
        "country": fields.String(
            description="Country", example="France", default="France"
        ),
    },
)

user_login_model = auth_ns.model(
    "UserLogin",
    {
        "email": fields.String(
            required=True,
            description="User email",
            example="jean.dupont@example.com",
            default="jean.dupont@example.com",
        ),
        "password": fields.String(
            required=True,
            description="Password",
            example="password",
            default="password",
        ),
    },
)

company_register_model = auth_ns.model(
    "CompanyRegister",
    {
        "name": fields.String(
            required=True,
            description="Company name",
            example="InnovateTech Solutions",
            default="InnovateTech Solutions",
        ),
        "industry": fields.String(
            required=True,
            description="Company industry",
            example="Software Development",
            default="Software Development",
        ),
        "description": fields.String(
            required=True,
            description="Company description",
            example="We are a cutting-edge software development company specializing in web and mobile applications. We create innovative solutions for businesses of all sizes.",
            default="We are a cutting-edge software development company specializing in web and mobile applications. We create innovative solutions for businesses of all sizes.",
        ),
        "email": fields.String(
            required=True,
            description="Company email (must be unique)",
            example="contact@innovatetech.com",
            default="contact@innovatetech.com",
        ),
        "password": fields.String(
            required=True,
            description="Password (minimum 6 characters)",
            example="companypass123",
            default="companypass123",
        ),
        "confirmPassword": fields.String(
            required=True,
            description="Confirm password (must match)",
            example="companypass123",
            default="companypass123",
        ),
        "website": fields.String(
            description="Company website",
            example="https://www.innovatetech.com",
            default="https://www.innovatetech.com",
        ),
        "phone": fields.String(
            description="Company phone number",
            example="+33 1 42 86 83 45",
            default="+33 1 42 86 83 45",
        ),
        "address": fields.String(
            description="Company address",
            example="42 Avenue des Champs-Élysées",
            default="42 Avenue des Champs-Élysées",
        ),
        "city": fields.String(description="City", example="Paris", default="Paris"),
        "country": fields.String(
            description="Country", example="France", default="France"
        ),
        "logo": fields.String(
            description="Company logo URL",
            example="https://www.innovatetech.com/logo.png",
            default="https://www.innovatetech.com/logo.png",
        ),
    },
)

company_login_model = auth_ns.model(
    "CompanyLogin",
    {
        "email": fields.String(
            required=True,
            description="Company email",
            example="contact@techcorp.example.com",
            default="contact@techcorp.example.com",
        ),
        "password": fields.String(
            required=True,
            description="Password",
            example="password",
            default="password",
        ),
    },
)

# Response models
auth_response_model = auth_ns.model(
    "AuthResponse",
    {
        "user": fields.Raw(description="User data (if user login/register)"),
        "company": fields.Raw(description="Company data (if company login/register)"),
        "token": fields.String(
            description="JWT authentication token - COPY THIS for Authorization!",
            example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTYzOTU4...",
        ),
    },
)

error_model = auth_ns.model(
    "Error",
    {
        "error": fields.String(description="Error type"),
        "message": fields.String(description="Error message"),
        "messages": fields.Raw(description="Detailed validation errors"),
    },
)


@auth_ns.route("/register/user")
class UserRegister(Resource):
    @auth_ns.expect(user_register_model)
    @auth_ns.response(201, "User registered successfully", auth_response_model)
    @auth_ns.response(400, "Validation error or email already exists", error_model)
    def post(self):
        """
        Register a new user

        After successful registration, copy the 'token' from the response.
        Then click 'Authorize' button above and paste: Bearer YOUR_TOKEN
        """
        try:
            # Validate and deserialize input
            data = UserRegisterSchema().load(request.json)

            # Check if user with this email already exists
            existing_user = User.find_by_email(data["email"])
            if existing_user:
                return {"error": "Email already registered"}, 400

            # Create new user
            user_id = User.create(data)

            # Get the created user
            user = User.find_by_id(user_id)

            # Generate authentication token
            token = generate_token(user_id, "user")

            # Return user data and token
            return {"user": UserSchema().dump(user), "token": token}, 201

        except ValidationError as err:
            return {"error": "Validation error", "messages": err.messages}, 400
        except Exception as e:
            return {"error": str(e)}, 500


@auth_ns.route("/register/company")
class CompanyRegister(Resource):
    @auth_ns.expect(company_register_model)
    @auth_ns.response(201, "Company registered successfully", auth_response_model)
    @auth_ns.response(400, "Validation error or email already exists", error_model)
    def post(self):
        """
        Register a new company

        After successful registration, copy the 'token' from the response.
        Then click 'Authorize' button above and paste: Bearer YOUR_TOKEN
        """
        try:
            # Validate and deserialize input
            data = CompanyRegisterSchema().load(request.json)

            # Check if company with this email already exists
            existing_company = Company.find_by_email(data["email"])
            if existing_company:
                return {"error": "Email already registered"}, 400

            # Create new company
            company_id = Company.create(data)

            # Get the created company
            company = Company.find_by_id(company_id)

            # Generate authentication token
            token = generate_token(company_id, "company")

            # Return company data and token
            return {"company": CompanySchema().dump(company), "token": token}, 201

        except ValidationError as err:
            return {"error": "Validation error", "messages": err.messages}, 400
        except Exception as e:
            return {"error": str(e)}, 500


@auth_ns.route("/login/user")
class UserLogin(Resource):
    @auth_ns.expect(user_login_model)
    @auth_ns.response(200, "Login successful", auth_response_model)
    @auth_ns.response(401, "Invalid credentials", error_model)
    def post(self):
        """
        Login for users

        Use the test account:
        Email: jean.dupont@example.com
        Password: password

        After successful login, copy the 'token' from the response.
        Then click 'Authorize' button above and paste: Bearer YOUR_TOKEN
        """
        try:
            # Validate and deserialize input
            data = UserLoginSchema().load(request.json)

            # Authenticate user
            user = User.authenticate(data["email"], data["password"])
            if not user:
                return {"error": "Invalid email or password"}, 401

            # Generate authentication token
            token = generate_token(user["_id"], "user")

            # Return user data and token
            return {"user": UserSchema().dump(user), "token": token}, 200

        except ValidationError as err:
            return {"error": "Validation error", "messages": err.messages}, 400
        except Exception as e:
            return {"error": str(e)}, 500


@auth_ns.route("/login/company")
class CompanyLogin(Resource):
    @auth_ns.expect(company_login_model)
    @auth_ns.response(200, "Login successful", auth_response_model)
    @auth_ns.response(401, "Invalid credentials", error_model)
    def post(self):
        """
        Login for companies

        Use the test account:
        Email: contact@techcorp.example.com
        Password: password

        After successful login, copy the 'token' from the response.
        Then click 'Authorize' button above and paste: Bearer YOUR_TOKEN
        """
        try:
            # Validate and deserialize input
            data = CompanyLoginSchema().load(request.json)

            # Authenticate company
            company = Company.authenticate(data["email"], data["password"])
            if not company:
                return {"error": "Invalid email or password"}, 401

            # Generate authentication token
            token = generate_token(company["_id"], "company")

            # Return company data and token
            return {"company": CompanySchema().dump(company), "token": token}, 200

        except ValidationError as err:
            return {"error": "Validation error", "messages": err.messages}, 400
        except Exception as e:
            return {"error": str(e)}, 500


# Keep the original Flask routes for backward compatibility
@auth_bp.route("/register/user", methods=["POST"])
def register_user():
    """Register a new user"""
    return UserRegister().post()


@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    """Register a new company"""
    return CompanyRegister().post()


@auth_bp.route("/login/user", methods=["POST"])
def login_user():
    """Login for users"""
    return UserLogin().post()


@auth_bp.route("/login/company", methods=["POST"])
def login_company():
    """Login for companies"""
    return CompanyLogin().post()
