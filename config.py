import os
import secrets
from datetime import timedelta

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _generate_secret_key():
    """Generate a secure random secret key."""
    return secrets.token_hex(32)


def _parse_cors_origins(origins_string):
    """Parse CORS origins from environment variable."""
    if not origins_string:
        return ["http://localhost:3000"]
    
    # Split by comma and clean up whitespace
    origins = [origin.strip() for origin in origins_string.split(",")]
    
    # Filter out empty strings
    origins = [origin for origin in origins if origin]
    
    return origins if origins else ["http://localhost:3000"]


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY") or _generate_secret_key()
    
    # MongoDB
    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/interimapp")
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or _generate_secret_key()
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))  # 1 hour default
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES", 30))  # 30 days default
    )
    JWT_ALGORITHM = "HS256"
    
    # CORS Configuration
    CORS_ORIGINS = _parse_cors_origins(
        os.environ.get("CORS_ORIGINS", "http://localhost:3000")
    )
    
    # Application Settings
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16MB
    
    # Pagination
    DEFAULT_PAGE_SIZE = int(os.environ.get("DEFAULT_PAGE_SIZE", 20))
    MAX_PAGE_SIZE = int(os.environ.get("MAX_PAGE_SIZE", 100))
    
    # Rate Limiting (requests per minute)
    RATE_LIMIT_DEFAULT = os.environ.get("RATE_LIMIT_DEFAULT", "100/minute")
    RATE_LIMIT_AUTH = os.environ.get("RATE_LIMIT_AUTH", "5/minute")
    
    # Email Configuration (for future use)
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    
    # File Upload Settings
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")
    ALLOWED_EXTENSIONS = {"txt", "pdf", "doc", "docx", "jpg", "jpeg", "png"}
    
    @staticmethod
    def validate_config():
        """Validate critical configuration settings."""
        errors = []
        
        # Check MongoDB URI format
        mongodb_uri = Config.MONGODB_URI
        if not mongodb_uri.startswith(("mongodb://", "mongodb+srv://")):
            errors.append("MONGODB_URI must start with 'mongodb://' or 'mongodb+srv://'")
        
        # Warn about default secrets in production
        if os.environ.get("FLASK_ENV") == "production":
            if not os.environ.get("SECRET_KEY"):
                errors.append("SECRET_KEY must be set in production")
            if not os.environ.get("JWT_SECRET_KEY"):
                errors.append("JWT_SECRET_KEY must be set in production")
        
        return errors


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    
    # More verbose logging in development
    LOG_LEVEL = "DEBUG"
    
    # Relaxed rate limiting for development
    RATE_LIMIT_DEFAULT = "1000/minute"
    RATE_LIMIT_AUTH = "50/minute"
    
    # Development-specific settings
    EXPLAIN_TEMPLATE_LOADING = False
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Strict settings for production
    LOG_LEVEL = "INFO"
    
    # Enhanced security headers for production
    SECURITY_HEADERS = {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    @staticmethod
    def validate_production_config():
        """Additional validation for production environment."""
        errors = Config.validate_config()
        
        # Production-specific checks
        required_env_vars = [
            "SECRET_KEY",
            "JWT_SECRET_KEY", 
            "MONGODB_URI"
        ]
        
        for var in required_env_vars:
            if not os.environ.get(var):
                errors.append(f"{var} is required in production")
        
        # Check for secure MongoDB connection in production
        mongodb_uri = os.environ.get("MONGODB_URI", "")
        if mongodb_uri.startswith("mongodb://localhost"):
            errors.append("Production should not use localhost MongoDB")
        
        return errors


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = True
    
    # Use separate test database
    MONGODB_URI = os.environ.get(
        "TEST_MONGODB_URI", "mongodb://localhost:27017/interimapp_test"
    )
    
    # Shorter token expiry for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Disable rate limiting in tests
    RATE_LIMIT_DEFAULT = "10000/minute"
    RATE_LIMIT_AUTH = "1000/minute"
    
    # Test-specific settings
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = "WARNING"  # Reduce noise in tests


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration class based on environment variable."""
    config_name = os.environ.get("FLASK_ENV", "default").lower()
    config_class = config.get(config_name, config["default"])
    
    # Validate configuration
    if config_name == "production":
        errors = ProductionConfig.validate_production_config()
    else:
        errors = Config.validate_config()
    
    if errors:
        raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
    
    return config_class


def get_upload_path():
    """Get the absolute path for file uploads."""
    upload_folder = Config.UPLOAD_FOLDER
    if not os.path.isabs(upload_folder):
        # Make relative paths relative to the application root
        import os.path
        upload_folder = os.path.join(os.path.dirname(__file__), upload_folder)
    
    # Create directory if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)
    
    return upload_folder


def is_allowed_file(filename):
    """Check if uploaded file has allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS