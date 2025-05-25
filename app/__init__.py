import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import time

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
    
    # Setup logging
    setup_logging(app)
    
    # Initialize CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['http://localhost:3000']),
            "supports_credentials": True,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
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
            app.db.command('ping')
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "timestamp": time.time()
            }), 200
        except Exception as e:
            return jsonify({
                "status": "unhealthy", 
                "database": "disconnected",
                "error": str(e)
            }), 503
    
    @app.route("/api/test", methods=["GET"])
    def test_api():
        return jsonify({"status": "API server is running"}), 200
    
    return app

def setup_logging(app):
    """Configure application logging"""
    logging.basicConfig(
        level=logging.INFO if not app.debug else logging.DEBUG,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    
    # Create logger for the app
    logger = logging.getLogger('interim_app')
    app.logger = logger

def init_db(app):
    """Initialize database connection with retry logic"""
    global mongodb_client, db
    
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            mongodb_client = MongoClient(
                app.config["MONGODB_URI"],
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,         # 10 second connection timeout
                maxPoolSize=50,                 # Connection pool size
                retryWrites=True
            )
            
            # Test the connection
            mongodb_client.admin.command('ping')
            
            db_name = app.config["MONGODB_URI"].split("/")[-1]
            db = mongodb_client[db_name]
            
            # Make instances available to the app
            app.mongodb_client = mongodb_client
            app.db = db
            
            app.logger.info("Database connection established successfully")
            return
            
        except ConnectionFailure as e:
            app.logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                app.logger.error("Failed to connect to database after all retries")
                raise

def setup_jwt_handlers(app):
    """Setup JWT error handlers"""
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token"}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Authorization token required"}), 401

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
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

def register_blueprints(app):
    """Register Flask blueprints"""
    from app.routes.auth import auth_bp
    from app.routes.companies import companies_bp
    from app.routes.jobs import jobs_bp
    from app.routes.users import users_bp
    
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(jobs_bp, url_prefix="/api/jobs")
    app.register_blueprint(companies_bp, url_prefix="/api/companies")
    app.register_blueprint(users_bp, url_prefix="/api/users")

def register_error_handlers(app):
    """Register comprehensive error handlers"""
    
    @app.errorhandler(400)
    def bad_request(e):
        app.logger.warning(f"Bad request: {str(e)}")
        return jsonify({"error": "Bad request", "message": str(e)}), 400
    
    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
    
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden", "message": "Insufficient permissions"}), 403
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "message": "Resource not found"}), 404
    
    @app.errorhandler(413)
    def request_too_large(e):
        return jsonify({"error": "Request too large", "message": "File size exceeds limit"}), 413
    
    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify({"error": "Too many requests", "message": "Rate limit exceeded"}), 429
    
    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"Internal server error: {str(e)}")
        return jsonify({"error": "Internal server error", "message": "Something went wrong"}), 500
    
    # Handle custom database errors
    from app.utils.db import DatabaseError, InvalidObjectIdError
    
    @app.errorhandler(DatabaseError)
    def handle_database_error(e):
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error", "message": "Please try again later"}), 500
    
    @app.errorhandler(InvalidObjectIdError)
    def handle_invalid_id_error(e):
        return jsonify({"error": "Invalid ID", "message": str(e)}), 400