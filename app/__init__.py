<<<<<<< HEAD
import logging
import time

from flask import Flask, jsonify, request
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
from flask import Flask, jsonify
=======
import logging
import time
import uuid
from urllib.parse import urlparse

from flask import Flask, jsonify, request, g
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api
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

<<<<<<< HEAD
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
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
    # Initialize CORS with more permissive settings
    CORS(app, resources={r"/api/*": {"origins": "*", "supports_credentials": True}})
=======
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
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)

    # Initialize JWT
    jwt.init_app(app)
    setup_jwt_handlers(app)

    # Initialize MongoDB with retry logic
    init_db(app)

<<<<<<< HEAD
    # Add request middleware
    setup_middleware(app)

    # Initialize Swagger API with expanded sections
    api = Api(
        app,
        version="1.0",
        title="🚀 InterimApp API",
        description="""
        <h2>Welcome to InterimApp API Documentation!</h2>
        <p>A comprehensive job search platform API for students and companies.</p>
        
        <h3>🔐 How to Use Authentication:</h3>
        <ol>
            <li><strong>Register/Login:</strong> Use the auth endpoints to create an account or login</li>
            <li><strong>Copy Token:</strong> From the response, copy the 'token' value</li>
            <li><strong>Authorize:</strong> Click the 🔒 "Authorize" button above</li>
            <li><strong>Enter Token:</strong> Paste: <code>Bearer YOUR_TOKEN_HERE</code></li>
            <li><strong>Test:</strong> Now you can use protected endpoints!</li>
        </ol>
        
        <h3>📝 How to Test Endpoints:</h3>
        <ol>
            <li><strong>Click "Try it out"</strong> on any endpoint</li>
            <li><strong>Modify the example data</strong> in the text fields</li>
            <li><strong>Click "Execute"</strong> to test</li>
            <li><strong>See the response</strong> below</li>
        </ol>
        
        <h3>📋 Test Accounts:</h3>
        <p><strong>User:</strong> jean.dupont@example.com / password</p>
        <p><strong>Company:</strong> contact@techcorp.example.com / password</p>
        
        <h3>🔄 Quick Start Flow:</h3>
        <p>1. Login as company → 2. Create a job → 3. Login as user → 4. Apply for job</p>
        """,
        doc="/api/docs/",
        prefix="/api",
        doc_expansion="full",
        # Enable "Try it out" by default
        default_swagger_ui_config={
            "tryItOutEnabled": True,
            "defaultModelsExpandDepth": 2,
            "defaultModelExpandDepth": 2,
            "displayRequestDuration": True,
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
        },
    )

    # Configure Swagger security with clear instructions
    api.authorizations = {
        "Bearer": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": """
                <h4>🔑 JWT Token Authentication</h4>
                <p>Enter your token in this format:</p>
                <code>Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...</code>
                <br><br>
                <p><strong>Steps:</strong></p>
                <ol>
                    <li>Login/Register using auth endpoints</li>
                    <li>Copy the "token" from response</li>
                    <li>Paste it here with "Bearer " prefix</li>
                </ol>
            """,
        }
    }

    # Register blueprints and namespaces
    register_blueprints(app, api)
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
    # Register blueprints
    register_blueprints(app)
=======
    # Add request middleware
    setup_middleware(app)

    # Register blueprints
    register_blueprints(app)
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)

    # Register error handlers
    register_error_handlers(app)

<<<<<<< HEAD
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
                        "version": "1.0.0",
                    }
                ),
                200,
            )
        except Exception as e:
            return (
                jsonify(
                    {"status": "unhealthy", "database": "disconnected", "error": str(e)}
                ),
                503,
            )

||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
    # Add a test endpoint to verify API connection
=======
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

>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)
    @app.route("/api/test", methods=["GET"])
    def test_api():
<<<<<<< HEAD
        return (
            jsonify(
                {
                    "status": "API server is running",
                    "message": "🎉 InterimApp backend is working!",
                    "endpoints": {"docs": "/api/docs/", "health": "/api/health"},
                }
            ),
            200,
        )

    # Redirect root to swagger docs with welcome message
    @app.route("/")
    def redirect_to_docs():
        return (
            jsonify(
                {
                    "message": "🚀 Welcome to InterimApp API!",
                    "documentation": "/api/docs/",
                    "health": "/api/health",
                    "test": "/api/test",
                    "tip": "Visit /api/docs/ for interactive API documentation",
                }
            ),
            200,
        )
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
        return jsonify({"status": "API server is running"}), 200
=======
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
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)

    return app


<<<<<<< HEAD
def setup_logging(app):
    """Configure application logging"""
    logging.basicConfig(
        level=logging.INFO if not app.debug else logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Create logger for the app
    logger = logging.getLogger("interim_app")
    app.logger = logger


||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
=======
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


>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)
def init_db(app):
<<<<<<< HEAD
    """Initialize database connection with retry logic"""
    global mongodb_client, db
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
    """Initialize database connection"""
    global mongodb_client, db
=======
    """Initialize database connection with retry logic"""
    max_retries = 3
    retry_delay = 1
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)

<<<<<<< HEAD
    max_retries = 3
    retry_delay = 1
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
    mongodb_client = MongoClient(app.config["MONGODB_URI"])
    db_name = app.config["MONGODB_URI"].split("/")[-1]
    db = mongodb_client[db_name]
=======
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
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)

<<<<<<< HEAD
    for attempt in range(max_retries):
        try:
            mongodb_client = MongoClient(
                app.config["MONGODB_URI"],
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,  # 10 second connection timeout
                maxPoolSize=50,  # Connection pool size
                retryWrites=True,
            )

            # Test the connection
            mongodb_client.admin.command("ping")

            db_name = app.config["MONGODB_URI"].split("/")[-1]
            db = mongodb_client[db_name]

            # Make instances available to the app
            app.mongodb_client = mongodb_client
            app.db = db

            app.logger.info("Database connection established successfully")
            return

        except ConnectionFailure as e:
            app.logger.warning(
                f"Database connection attempt {attempt + 1} failed: {str(e)}"
            )
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                app.logger.error("Failed to connect to database after all retries")
                raise
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
    # Make the db instance available to the app
    app.mongodb_client = mongodb_client
    app.db = db
=======
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
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


<<<<<<< HEAD
def setup_jwt_handlers(app):
    """Setup JWT error handlers"""

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"error": "Token has expired", "message": "Please login again"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"error": "Invalid token", "message": "Please provide a valid token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "error": "Authorization token required",
                    "message": "Please login first",
                }
            ),
            401,
        )


def setup_middleware(app):
    """Setup request/response middleware"""

    @app.before_request
    def log_request_info():
        if app.debug:
            app.logger.debug(f"{request.method} {request.url}")

    @app.before_request
    def limit_request_size():
        # Limit request size to 16MB
        if request.content_length and request.content_length > 16 * 1024 * 1024:
            return jsonify({"error": "Request too large"}), 413

    @app.after_request
    def after_request(response):
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response


def register_blueprints(app, api):
    """Register Flask blueprints and Swagger namespaces"""

    # Import and register all namespaces for Swagger
    from app.routes.auth import auth_ns
    from app.routes.companies import companies_ns
    from app.routes.jobs import jobs_ns
    from app.routes.users import users_ns

    # Add namespaces to API (this creates the Swagger documentation)
    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(users_ns, path="/users")
    api.add_namespace(companies_ns, path="/companies")
    api.add_namespace(jobs_ns, path="/jobs")

    # Register traditional blueprints for backward compatibility
    from app.routes.auth import auth_bp
    from app.routes.companies import companies_bp
    from app.routes.jobs import jobs_bp
    from app.routes.users import users_bp
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
def register_blueprints(app):
    """Register Flask blueprints"""
    from app.routes.auth import auth_bp
    from app.routes.companies import companies_bp
    from app.routes.jobs import jobs_bp
    from app.routes.users import users_bp
=======
def register_blueprints(app):
    """Register Flask blueprints"""
    try:
        from app.routes.auth import auth_bp
        from app.routes.companies import companies_bp
        from app.routes.jobs import jobs_bp
        from app.routes.users import users_bp
        from app.routes.applications import applications_bp
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)

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
<<<<<<< HEAD
        app.logger.warning(f"Bad request: {str(e)}")
        return jsonify({"error": "Bad request", "message": str(e)}), 400
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
        return {"error": "Bad request", "message": str(e)}, 400
=======
        app.logger.warning(f"[{g.get('request_id')}] Bad request: {str(e)}")
        return jsonify({
            "error": "Bad request", 
            "message": str(e),
            "request_id": g.get('request_id')
        }), 400
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)

    @app.errorhandler(401)
    def unauthorized(e):
<<<<<<< HEAD
        return (
            jsonify({"error": "Unauthorized", "message": "Authentication required"}),
            401,
        )
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
        return {"error": "Unauthorized", "message": str(e)}, 401
=======
        return jsonify({
            "error": "Unauthorized", 
            "message": "Authentication required",
            "request_id": g.get('request_id')
        }), 401
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)

    @app.errorhandler(403)
    def forbidden(e):
<<<<<<< HEAD
        return (
            jsonify({"error": "Forbidden", "message": "Insufficient permissions"}),
            403,
        )
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
        return {"error": "Forbidden", "message": str(e)}, 403
=======
        return jsonify({
            "error": "Forbidden", 
            "message": "Insufficient permissions",
            "request_id": g.get('request_id')
        }), 403
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)

    @app.errorhandler(404)
    def not_found(e):
<<<<<<< HEAD
        return jsonify({"error": "Not found", "message": "Resource not found"}), 404

    @app.errorhandler(413)
    def request_too_large(e):
        return (
            jsonify(
                {"error": "Request too large", "message": "File size exceeds limit"}
            ),
            413,
        )

    @app.errorhandler(429)
    def too_many_requests(e):
        return (
            jsonify({"error": "Too many requests", "message": "Rate limit exceeded"}),
            429,
        )
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
        return {"error": "Not found", "message": str(e)}, 404
=======
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
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)

    @app.errorhandler(500)
    def internal_server_error(e):
<<<<<<< HEAD
        app.logger.error(f"Internal server error: {str(e)}")
        return (
            jsonify(
                {"error": "Internal server error", "message": "Something went wrong"}
            ),
            500,
        )

    # Handle custom database errors
    try:
        from app.utils.db import DatabaseError, InvalidObjectIdError

        @app.errorhandler(DatabaseError)
        def handle_database_error(e):
            app.logger.error(f"Database error: {str(e)}")
            return (
                jsonify(
                    {"error": "Database error", "message": "Please try again later"}
                ),
                500,
            )

        @app.errorhandler(InvalidObjectIdError)
        def handle_invalid_id_error(e):
            return jsonify({"error": "Invalid ID", "message": str(e)}), 400

    except ImportError:
        # If custom exceptions don't exist yet, skip them
        pass
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
        return {"error": "Internal server error", "message": str(e)}, 500
=======
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
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)
