import logging
from datetime import timedelta
from typing import Dict, Optional, Union

from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from passlib.hash import pbkdf2_sha256

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Custom exception for security operations"""

    pass


def hash_password(password: str) -> str:
    """Hash a password using pbkdf2_sha256"""
    if not password:
        raise SecurityError("Password cannot be empty")

    try:
        hashed = pbkdf2_sha256.hash(password)
        logger.debug("Password hashed successfully")
        return hashed

    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise SecurityError(f"Failed to hash password: {str(e)}") from e


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    if not password or not hashed_password:
        return False

    try:
        is_valid = pbkdf2_sha256.verify(password, hashed_password)
        logger.debug(f"Password verification result: {is_valid}")
        return is_valid

    except (ValueError, Exception) as e:
        logger.warning(f"Password verification failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during password verification: {str(e)}")
        return False


def generate_tokens(
    user_id: Union[str, int], user_type: str, additional_claims: Optional[Dict] = None
) -> Dict[str, str]:
    """Generate access and refresh JWT tokens"""
    try:
        # Get token expiration from config
        access_expires = current_app.config.get(
            "JWT_ACCESS_TOKEN_EXPIRES", timedelta(hours=1)
        )
        refresh_expires = current_app.config.get(
            "JWT_REFRESH_TOKEN_EXPIRES", timedelta(days=30)
        )

        # Prepare claims
        claims = {"user_type": user_type}
        if additional_claims:
            claims.update(additional_claims)

        # Create tokens
        access_token = create_access_token(
            identity=str(user_id),
            additional_claims=claims,
            expires_delta=access_expires,
        )

        refresh_token = create_refresh_token(
            identity=str(user_id),
            additional_claims=claims,
            expires_delta=refresh_expires,
        )

        logger.debug(f"Generated tokens for user: {user_id}, type: {user_type}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": int(access_expires.total_seconds()),
        }

    except Exception as e:
        logger.error(f"Error generating tokens for user {user_id}: {str(e)}")
        raise SecurityError(f"Failed to generate tokens: {str(e)}") from e


def generate_token(user_id: Union[str, int], user_type: str) -> str:
    """Generate a single access token (backward compatibility)"""
    try:
        tokens = generate_tokens(user_id, user_type)
        return tokens["access_token"]

    except SecurityError:
        # Re-raise security errors
        raise
    except Exception as e:
        logger.error(f"Error generating single token: {str(e)}")
        raise SecurityError(f"Failed to generate token: {str(e)}") from e


def validate_password_strength(password: str) -> Dict[str, Union[bool, str]]:
    """Validate password strength and return feedback"""
    if not password:
        return {"valid": False, "message": "Password cannot be empty"}

    issues = []

    # Length check
    if len(password) < 6:
        issues.append("at least 6 characters")

    # Character type checks
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    # For student project, keep requirements simple
    if not (has_lower or has_upper):
        issues.append("at least one letter")

    if not has_digit:
        issues.append("at least one number")

    if issues:
        return {"valid": False, "message": f"Password must contain {', '.join(issues)}"}

    return {"valid": True, "message": "Password is strong"}


def sanitize_user_data(user_data: Dict) -> Dict:
    """Remove sensitive fields from user data before sending to client"""
    sensitive_fields = ["password", "hashed_password", "_password"]

    sanitized = user_data.copy()

    for field in sensitive_fields:
        sanitized.pop(field, None)

    return sanitized
