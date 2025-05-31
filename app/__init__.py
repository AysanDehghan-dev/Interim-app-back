import logging
import time
import uuid
from urllib.parse import urlparse

from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from config import get_config

# Initialize extensions
jwt = JWTManager()

# App constants
APP_VERSION = "1.0.0"
APP_NAME = "InterimApp"


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Load configuration
    app_config = get_config()
    app.config.from_object(app_config)

    # Validate required configuration
    validate_config(app)

    # Setup logging
    setup_logging(app)

    # Initialize CORS
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config.get("CORS_ORIGINS", ["http://localhost:3000"]),
                "supports_credentials": True,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Request-ID"],
            }
        },
    )

    # Initialize JWT
    jwt.init_app(app)
    setup_jwt_handlers(app)

    # Initialize MongoDB with retry logic
    init_db(app)

    # Add request middleware
    setup_middleware(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        try:
            # Test database connection
            app.db.command("ping")
            return (
                jsonify(
                    {
                        "status": "healthy",
                        "database": "connected",
                        "timestamp": time.time(),
                        "version": APP_VERSION,
                        "app": APP_NAME,
                    }
                ),
                200,
            )
        except Exception as e:
            app.logger.error(f"Health check failed: {str(e)}")
            return (
                jsonify(
                    {
                        "status": "unhealthy", 
                        "database": "disconnected", 
                        "error": str(e),
                        "version": APP_VERSION,
                    }
                ),
                503,
            )

    @app.route("/api/test", methods=["GET"])
    def test_api():
        return (
            jsonify(
                {
                    "status": "API server is running",
                    "message": f"🎉 {APP_NAME} backend is working!",
                    "version": APP_VERSION,
                    "request_id": g.get('request_id'),
                    "endpoints": {
                        "health": "/api/health",
                        "auth": "/api/auth",
                        "jobs": "/api/jobs",
                        "companies": "/api/companies",
                        "users": "/api/users",
                        "applications": "/api/applications"
                    },
                }
            ),
            200,
        )

    # Root endpoint
    @app.route("/")
    def root():
        return (
            jsonify(
                {
                    "message": f"🚀 Welcome to {APP_NAME} API!",
                    "version": APP_VERSION,
                    "endpoints": {
                        "health": "/api/health",
                        "test": "/api/test",
                        "docs": "/api/docs"  # For future API documentation
                    }
                }
            ),
            200,
        )

    return app


def validate_config(app):
    """Validate required configuration exists"""
    required_config = ['MONGODB_URI', 'JWT_SECRET_KEY']
    
    for config_key in required_config:
        if not app.config.get(config_key):
            raise ValueError(f"Missing required configuration: {config_key}")
    
    app.logger.info("Configuration validation passed")


def setup_logging(app):
    """Configure application logging"""
    log_level = logging.DEBUG if app.debug else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Create logger for the app
    logger = logging.getLogger(APP_NAME.lower())
    app.logger = logger
    
    app.logger.info(f"Logging initialized - Level: {logging.getLevelName(log_level)}")


def init_db(app):
    """Initialize database connection with retry logic"""
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            # Parse database name from URI properly
            parsed_uri = urlparse(app.config["MONGODB_URI"])
            db_name = parsed_uri.path.lstrip('/') or 'interimapp'  # fallback name
            
            mongodb_client = MongoClient(
                app.config["MONGODB_URI"],
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,  # 10 second connection timeout
                maxPoolSize=50,  # Connection pool size
                retryWrites=True,
            )

            # Test the connection
            mongodb_client.admin.command("ping")
            
            db = mongodb_client[db_name]

            # Make instances available to the app
            app.mongodb_client = mongodb_client
            app.db = db

            app.logger.info(f"Database connection established - DB: {db_name}")
            return

        except ConnectionFailure as e:
            app.logger.warning(
                f"Database connection attempt {attempt + 1}/{max_retries} failed: {str(e)}"
            )
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                app.logger.error("Failed to connect to database after all retries")
                raise
        except Exception as e:
            app.logger.error(f"Unexpected database error: {str(e)}")
            raise


def setup_jwt_handlers(app):
    """Setup JWT error handlers"""

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({
                "error": "Token has expired", 
                "message": "Please login again",
                "request_id": g.get('request_id')
            }),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({
                "error": "Invalid token", 
                "message": "Please provide a valid token",
                "request_id": g.get('request_id')
            }),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify({
                "error": "Authorization token required",
                "message": "Please login first",
                "request_id": g.get('request_id')
            }),
            401,
        )


def setup_middleware(app):
    """Setup request/response middleware"""

    @app.before_request
    def add_request_id():
        """Add unique request ID for tracking"""
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))

    @app.before_request
    def log_request_info():
        """Log request information"""
        if app.debug:
            app.logger.debug(f"[{g.request_id}] {request.method} {request.url}")

    @app.before_request
    def limit_request_size():
        """Limit request size to prevent abuse"""
        max_size = 16 * 1024 * 1024  # 16MB
        if request.content_length and request.content_length > max_size:
            app.logger.warning(f"[{g.request_id}] Request too large: {request.content_length} bytes")
            return jsonify({
                "error": "Request too large", 
                "message": f"Maximum size is {max_size // (1024*1024)}MB",
                "request_id": g.request_id
            }), 413

    @app.after_request
    def after_request(response):
        """Add security headers and request ID to response"""
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Request-ID"] = g.get('request_id', '')
        
        # Log response in debug mode
        if app.debug:
            app.logger.debug(f"[{g.request_id}] Response: {response.status_code}")
        
        return response


def register_blueprints(app):
    """Register Flask blueprints"""
    try:
        from app.routes.auth import auth_bp
        from app.routes.companies import companies_bp
        from app.routes.jobs import jobs_bp
        from app.routes.users import users_bp
        from app.routes.applications import applications_bp

        app.register_blueprint(auth_bp, url_prefix="/api/auth")
        app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
        app.register_blueprint(companies_bp, url_prefix="/api/companies")
        app.register_blueprint(users_bp, url_prefix="/api/users")
        app.register_blueprint(applications_bp, url_prefix="/api/applications")
        
        app.logger.info("All blueprints registered successfully")
        
    except ImportError as e:
        app.logger.error(f"Failed to import blueprint: {str(e)}")
        # For development - continue without the missing blueprint
        if app.debug:
            app.logger.warning("Continuing in debug mode without all blueprints")
        else:
            raise


def register_error_handlers(app):
    """Register comprehensive error handlers"""

    @app.errorhandler(400)
    def bad_request(e):
        app.logger.warning(f"[{g.get('request_id')}] Bad request: {str(e)}")
        return jsonify({
            "error": "Bad request", 
            "message": str(e),
            "request_id": g.get('request_id')
        }), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({
            "error": "Unauthorized", 
            "message": "Authentication required",
            "request_id": g.get('request_id')
        }), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({
            "error": "Forbidden", 
            "message": "Insufficient permissions",
            "request_id": g.get('request_id')
        }), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "error": "Not found", 
            "message": "Resource not found",
            "request_id": g.get('request_id')
        }), 404

    @app.errorhandler(413)
    def request_too_large(e):
        return jsonify({
            "error": "Request too large", 
            "message": "File size exceeds limit",
            "request_id": g.get('request_id')
        }), 413

    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify({
            "error": "Too many requests", 
            "message": "Rate limit exceeded",
            "request_id": g.get('request_id')
        }), 429

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"[{g.get('request_id')}] Internal server error: {str(e)}")
        return jsonify({
            "error": "Internal server error", 
            "message": "Something went wrong" if not app.debug else str(e),
            "request_id": g.get('request_id')
        }), 500

    # Handle custom database errors (if they exist)
    try:
        from app.utils.db import DatabaseError, InvalidObjectIdError

        @app.errorhandler(DatabaseError)
        def handle_database_error(e):
            app.logger.error(f"[{g.get('request_id')}] Database error: {str(e)}")
            return jsonify({
                "error": "Database error", 
                "message": "Please try again later",
                "request_id": g.get('request_id')
            }), 500

        @app.errorhandler(InvalidObjectIdError)
        def handle_invalid_id_error(e):
            return jsonify({
                "error": "Invalid ID", 
                "message": str(e),
                "request_id": g.get('request_id')
            }), 400

    except ImportError:
        # Custom exceptions don't exist yet - that's fine
        app.logger.debug("Custom database exceptions not found - skipping handlers")
        pass