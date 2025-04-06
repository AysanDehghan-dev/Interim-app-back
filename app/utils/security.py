from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token
import datetime

def hash_password(password):
    """
    Hash a password using pbkdf2_sha256
    """
    return pbkdf2_sha256.hash(password)

def verify_password(password, hashed_password):
    """
    Verify a password against its hash
    """
    return pbkdf2_sha256.verify(password, hashed_password)

def generate_token(user_id, user_type):
    """
    Generate a JWT token with user information
    """
    # Set token expiration to 1 day
    expires = datetime.timedelta(days=1)
    
    # Create access token with user ID and type (user/company)
    token = create_access_token(
        identity=str(user_id),
        additional_claims={"user_type": user_type},
        expires_delta=expires
    )
    
    return token
    