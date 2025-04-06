from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models.user import User
from app.models.company import Company
from app.schemas.user_schema import UserLoginSchema, UserRegisterSchema, UserSchema
from app.schemas.company_schema import CompanyLoginSchema, CompanyRegisterSchema, CompanySchema
from app.utils.security import generate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register/user', methods=['POST'])
def register_user():
    """Register a new user"""
    try:
        # Validate and deserialize input
        data = UserRegisterSchema().load(request.json)
        
        # Check if user with this email already exists
        existing_user = User.find_by_email(data['email'])
        if existing_user:
            return jsonify({"error": "Email already registered"}), 400
        
        # Create new user
        user_id = User.create(data)
        
        # Get the created user
        user = User.find_by_id(user_id)
        
        # Generate authentication token
        token = generate_token(user_id, 'user')
        
        # Return user data and token
        return jsonify({
            "user": UserSchema().dump(user),
            "token": token
        }), 201
    
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    """Register a new company"""
    try:
        # Validate and deserialize input
        data = CompanyRegisterSchema().load(request.json)
        
        # Check if company with this email already exists
        existing_company = Company.find_by_email(data['email'])
        if existing_company:
            return jsonify({"error": "Email already registered"}), 400
        
        # Create new company
        company_id = Company.create(data)
        
        # Get the created company
        company = Company.find_by_id(company_id)
        
        # Generate authentication token
        token = generate_token(company_id, 'company')
        
        # Return company data and token
        return jsonify({
            "company": CompanySchema().dump(company),
            "token": token
        }), 201
    
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/login/user', methods=['POST'])
def login_user():
    """Login for users"""
    try:
        # Validate and deserialize input
        data = UserLoginSchema().load(request.json)
        
        # Authenticate user
        user = User.authenticate(data['email'], data['password'])
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Generate authentication token
        token = generate_token(user['_id'], 'user')
        
        # Return user data and token
        return jsonify({
            "user": UserSchema().dump(user),
            "token": token
        }), 200
    
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/login/company', methods=['POST'])
def login_company():
    """Login for companies"""
    try:
        # Validate and deserialize input
        data = CompanyLoginSchema().load(request.json)
        
        # Authenticate company
        company = Company.authenticate(data['email'], data['password'])
        if not company:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Generate authentication token
        token = generate_token(company['_id'], 'company')
        
        # Return company data and token
        return jsonify({
            "company": CompanySchema().dump(company),
            "token": token
        }), 200
    
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500