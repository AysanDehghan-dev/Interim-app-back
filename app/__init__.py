from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from config import get_config

# Initialize extensions
jwt = JWTManager()
mongodb_client = None
db = None


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Load configuration
    app_config = get_config()
    app.config.from_object(app_config)

    # Initialize CORS with more permissive settings
    CORS(app, resources={r"/api/*": {"origins": "*", "supports_credentials": True}})

    # Initialize JWT
    jwt.init_app(app)

    # Initialize MongoDB
    init_db(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Add a test endpoint to verify API connection
    @app.route("/api/test", methods=["GET"])
    def test_api():
        return jsonify({"status": "API server is running"}), 200

    return app


def init_db(app):
    """Initialize database connection"""
    global mongodb_client, db

    mongodb_client = MongoClient(app.config["MONGODB_URI"])
    db_name = app.config["MONGODB_URI"].split("/")[-1]
    db = mongodb_client[db_name]

    # Make the db instance available to the app
    app.mongodb_client = mongodb_client
    app.db = db


def register_blueprints(app):
    """Register Flask blueprints"""
    from app.routes.auth import auth_bp
    from app.routes.jobs import jobs_bp
    from app.routes.companies import companies_bp
    from app.routes.users import users_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
    app.register_blueprint(companies_bp, url_prefix="/api/companies")
    app.register_blueprint(users_bp, url_prefix="/api/users")


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(400)
    def bad_request(e):
        return {"error": "Bad request", "message": str(e)}, 400

    @app.errorhandler(401)
    def unauthorized(e):
        return {"error": "Unauthorized", "message": str(e)}, 401

    @app.errorhandler(403)
    def forbidden(e):
        return {"error": "Forbidden", "message": str(e)}, 403

    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Not found", "message": str(e)}, 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return {"error": "Internal server error", "message": str(e)}, 500
