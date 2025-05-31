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
from app.models.application import Application
from app.models.user import User
from app.schemas.user import UserSchema, UserUpdateSchema, ExperienceSchema, EducationSchema
from app.schemas.application import ApplicationSchema
from app.utils.decorators import handle_errors, require_user_type, validate_pagination, validate_json
from app.utils.response_helpers import success_response, paginated_response, sanitize_response_data
from app.utils.route_helpers import populate_application_data
from app.utils.db import ensure_document_exists

users_bp = Blueprint("users", __name__)

# Create namespace for swagger documentation
users_ns = Namespace(
    "users", description="User operations - Requires user authentication"
)

# Define models for swagger documentation
user_profile_update_model = users_ns.model(
    "UserProfileUpdate",
    {
        "firstName": fields.String(
            description="User first name", example="Marie", default="Marie"
        ),
        "lastName": fields.String(
            description="User last name", example="Laurent", default="Laurent"
        ),
        "phone": fields.String(
            description="Phone number",
            example="+33 6 45 67 89 12",
            default="+33 6 45 67 89 12",
        ),
        "address": fields.String(
            description="Home address",
            example="15 Boulevard Saint-Germain",
            default="15 Boulevard Saint-Germain",
        ),
        "city": fields.String(description="City", example="Paris", default="Paris"),
        "country": fields.String(
            description="Country", example="France", default="France"
        ),
        "profilePicture": fields.String(
            description="Profile picture URL",
            example="https://randomuser.me/api/portraits/women/5.jpg",
            default="https://randomuser.me/api/portraits/women/5.jpg",
        ),
        "skills": fields.List(
            fields.String,
            description="List of professional skills",
            example=[
                "JavaScript",
                "React.js",
                "Node.js",
                "Python",
                "MongoDB",
                "Git",
                "Agile/Scrum",
                "Problem Solving",
            ],
            default=[
                "JavaScript",
                "React.js",
                "Node.js",
                "Python",
                "MongoDB",
                "Git",
                "Agile/Scrum",
                "Problem Solving",
            ],
        ),
    },
)

experience_model = users_ns.model(
    "Experience",
    {
        "title": fields.String(
            required=True,
            description="Job title",
            example="Full Stack Developer",
            default="Full Stack Developer",
        ),
        "company": fields.String(
            required=True,
            description="Company name",
            example="Digital Solutions Inc.",
            default="Digital Solutions Inc.",
        ),
        "location": fields.String(
            description="Work location",
            example="Paris, France",
            default="Paris, France",
        ),
        "startDate": fields.DateTime(
            required=True,
            description="Employment start date",
            example="2022-03-01T00:00:00Z",
            default="2022-03-01T00:00:00Z",
        ),
        "endDate": fields.DateTime(
            description="Employment end date (leave empty if current)",
            example="2024-12-31T00:00:00Z",
            default="2024-12-31T00:00:00Z",
        ),
        "current": fields.Boolean(
            description="Currently working here", example=False, default=False
        ),
        "description": fields.String(
            description="Detailed job description and achievements",
            example="Developed and maintained web applications using React.js and Node.js. Led a team of 3 junior developers. Implemented CI/CD pipelines that reduced deployment time by 40%. Successfully delivered 15+ projects on time and within budget.",
            default="Developed and maintained web applications using React.js and Node.js. Led a team of 3 junior developers. Implemented CI/CD pipelines that reduced deployment time by 40%. Successfully delivered 15+ projects on time and within budget.",
        ),
    },
)

education_model = users_ns.model(
    "Education",
    {
        "institution": fields.String(
            required=True,
            description="Educational institution name",
            example="École Polytechnique",
            default="École Polytechnique",
        ),
        "degree": fields.String(
            required=True,
            description="Degree obtained",
            example="Master of Science",
            default="Master of Science",
        ),
        "field": fields.String(
            required=True,
            description="Field of study",
            example="Computer Science and Engineering",
            default="Computer Science and Engineering",
        ),
        "startDate": fields.DateTime(
            required=True,
            description="Start date of studies",
            example="2018-09-01T00:00:00Z",
            default="2018-09-01T00:00:00Z",
        ),
        "endDate": fields.DateTime(
            description="End date of studies (leave empty if ongoing)",
            example="2022-06-30T00:00:00Z",
            default="2022-06-30T00:00:00Z",
        ),
        "current": fields.Boolean(
            description="Currently studying", example=False, default=False
        ),
        "description": fields.String(
            description="Additional details about the education",
            example="Specialized in software engineering and artificial intelligence. Graduated Magna Cum Laude with a thesis on machine learning applications in web development.",
            default="Specialized in software engineering and artificial intelligence. Graduated Magna Cum Laude with a thesis on machine learning applications in web development.",
        ),
    },
)

error_model = users_ns.model(
    "Error",
    {
        "error": fields.String(description="Error type"),
        "message": fields.String(description="Error message"),
    },
)


@users_ns.route("/profile")
class UserProfile(Resource):
    @users_ns.doc("get_user_profile", security="Bearer")
    @users_ns.response(200, "Success - User profile data")
    @users_ns.response(401, "Authentication required", error_model)
    @users_ns.response(403, "Access denied - Users only", error_model)
    @jwt_required()
    def get(self):
        """Get the authenticated user's profile"""
        try:
            # Check if the authenticated user is a regular user
            claims = get_jwt()
            user_type = claims.get("user_type", "")

            if user_type != "user":
                return {"error": "Access denied"}, 403

            # Get the authenticated user ID
            user_id = get_jwt_identity()

            # Get the user
            user = User.find_by_id(user_id)

            if not user:
                return {"error": "User not found"}, 404

            return UserSchema().dump(user), 200

        except Exception as e:
            return {"error": str(e)}, 500

    @users_ns.expect(user_profile_update_model)
    @users_ns.doc("update_user_profile", security="Bearer")
    @users_ns.response(200, "Profile updated successfully")
    @users_ns.response(400, "Validation error", error_model)
    @users_ns.response(401, "Authentication required", error_model)
    @users_ns.response(403, "Access denied - Users only", error_model)
    @jwt_required()
    def put(self):
        """Update the authenticated user's profile"""
        try:
            # Check if the authenticated user is a regular user
            claims = get_jwt()
            user_type = claims.get("user_type", "")

            if user_type != "user":
                return {"error": "Access denied"}, 403

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

            return UserSchema().dump(updated_user), 200

        except ValidationError as err:
            return {"error": "Validation error", "messages": err.messages}, 400
        except Exception as e:
            return {"error": str(e)}, 500


@users_ns.route("/applications")
class UserApplications(Resource):
    @users_ns.doc("get_user_applications", security="Bearer")
    @users_ns.response(200, "Success - List of user applications with job details")
    @users_ns.response(401, "Authentication required", error_model)
    @users_ns.response(403, "Access denied - Users only", error_model)
    @jwt_required()
    def get(self):
        """Get the authenticated user's job applications"""
        try:
            # Check if the authenticated user is a regular user
            claims = get_jwt()
            user_type = claims.get("user_type", "")

            if user_type != "user":
                return {"error": "Access denied"}, 403

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

            return ApplicationSchema(many=True).dump(applications), 200

        except Exception as e:
            return {"error": str(e)}, 500


@users_ns.route("/experience")
class UserExperience(Resource):
    @users_ns.expect(experience_model)
    @users_ns.doc("add_user_experience", security="Bearer")
    @users_ns.response(200, "Experience added successfully")
    @users_ns.response(400, "Validation error", error_model)
    @users_ns.response(401, "Authentication required", error_model)
    @users_ns.response(403, "Access denied - Users only", error_model)
    @jwt_required()
    def post(self):
        """Add work experience to user profile"""
        try:
            # Check if the authenticated user is a regular user
            claims = get_jwt()
            user_type = claims.get("user_type", "")

            if user_type != "user":
                return {"error": "Access denied"}, 403

            # Get the authenticated user ID
            user_id = get_jwt_identity()

            # Get experience data from request
            experience_data = request.json

            if not experience_data:
                return {"error": "Experience data is required"}, 400

            # Add experience to user
            experience_id = User.add_experience(user_id, experience_data)

            if not experience_id:
                return {"error": "Failed to add experience"}, 400

            # Get the updated user
            updated_user = User.find_by_id(user_id)

            return UserSchema().dump(updated_user), 200

        except Exception as e:
            return {"error": str(e)}, 500


@users_ns.route("/education")
class UserEducation(Resource):
    @users_ns.expect(education_model)
    @users_ns.doc("add_user_education", security="Bearer")
    @users_ns.response(200, "Education added successfully")
    @users_ns.response(400, "Validation error", error_model)
    @users_ns.response(401, "Authentication required", error_model)
    @users_ns.response(403, "Access denied - Users only", error_model)
    @jwt_required()
    def post(self):
        """Add education to user profile"""
        try:
            # Check if the authenticated user is a regular user
            claims = get_jwt()
            user_type = claims.get("user_type", "")

            if user_type != "user":
                return {"error": "Access denied"}, 403

            # Get the authenticated user ID
            user_id = get_jwt_identity()

            # Get education data from request
            education_data = request.json

            if not education_data:
                return {"error": "Education data is required"}, 400

            # Add education to user
            education_id = User.add_education(user_id, education_data)

            if not education_id:
                return {"error": "Failed to add education"}, 400

            # Get the updated user
            updated_user = User.find_by_id(user_id)

            return UserSchema().dump(updated_user), 200

        except Exception as e:
            return {"error": str(e)}, 500


# Keep the original Flask routes for backward compatibility
@users_bp.route("/profile", methods=["GET"])
@handle_errors
@require_user_type("user")
def get_profile(current_user_id, current_user_type):
    """Get the authenticated user's profile"""
<<<<<<< HEAD
    return UserProfile().get()
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
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
=======
    user = ensure_document_exists("users", current_user_id)
    
    return success_response(UserSchema().dump(sanitize_response_data(user)))
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


@users_bp.route("/profile", methods=["PUT"])
@handle_errors
@require_user_type("user")
@validate_json(UserUpdateSchema)
def update_profile(current_user_id, current_user_type, validated_data):
    """Update the authenticated user's profile"""
<<<<<<< HEAD
    return UserProfile().put()
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
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
=======
    # Update user
    User.update(current_user_id, validated_data)
    
    # Get the updated user
    updated_user = ensure_document_exists("users", current_user_id)
    
    return success_response(
        UserSchema().dump(sanitize_response_data(updated_user)),
        message="Profile updated successfully"
    )
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


@users_bp.route("/applications", methods=["GET"])
@handle_errors
@require_user_type("user")
@validate_pagination
def get_applications(current_user_id, current_user_type, pagination):
    """Get the authenticated user's job applications"""
<<<<<<< HEAD
    return UserApplications().get()
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
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
=======
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
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


@users_bp.route("/experience", methods=["POST"])
@handle_errors
@require_user_type("user")
@validate_json(ExperienceSchema)
def add_experience(current_user_id, current_user_type, validated_data):
    """Add experience to user profile"""
<<<<<<< HEAD
    return UserExperience().post()
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
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
=======
    # Add experience to user
    experience_id = User.add_experience(current_user_id, validated_data)
    
    # Get the updated user
    updated_user = ensure_document_exists("users", current_user_id)
    
    return success_response(
        UserSchema().dump(sanitize_response_data(updated_user)),
        message="Experience added successfully"
    )
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


@users_bp.route("/education", methods=["POST"])
@handle_errors
@require_user_type("user")
@validate_json(EducationSchema)
def add_education(current_user_id, current_user_type, validated_data):
    """Add education to user profile"""
<<<<<<< HEAD
    return UserEducation().post()
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
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
=======
    # Add education to user
    education_id = User.add_education(current_user_id, validated_data)
    
    # Get the updated user
    updated_user = ensure_document_exists("users", current_user_id)
    
    return success_response(
        UserSchema().dump(sanitize_response_data(updated_user)),
        message="Education added successfully"
    )
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)
