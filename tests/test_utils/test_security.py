import pytest
import jwt
from datetime import datetime, timedelta
from bson import ObjectId

from app.utils.security import hash_password, verify_password, generate_token

def test_hash_password():
    # Test password hashing
    password = 'test_password'
    hashed = hash_password(password)
    
    # Verify result is a string and not the original password
    assert isinstance(hashed, str)
    assert hashed != password
    
    # Test different passwords have different hashes
    another_password = 'another_password'
    another_hash = hash_password(another_password)
    assert hashed != another_hash

def test_verify_password():
    # Test password verification
    password = 'test_password'
    hashed = hash_password(password)
    
    # Verify correct password
    assert verify_password(password, hashed) is True
    
    # Verify incorrect password
    assert verify_password('wrong_password', hashed) is False
    
    # Verify against empty or None values
    assert verify_password('', hashed) is False
    assert verify_password(None, hashed) is False

def test_generate_token(app):
    with app.app_context():
        # Test token generation for user
        user_id = str(ObjectId())
        user_token = generate_token(user_id, 'user')
        
        # Verify token is a string
        assert isinstance(user_token, str)
        
        # Decode token and verify claims
        decoded = jwt.decode(
            user_token, 
            app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        assert decoded['sub'] == user_id
        assert decoded['user_type'] == 'user'
        assert 'exp' in decoded
        
        # Test token generation for company
        company_id = str(ObjectId())
        company_token = generate_token(company_id, 'company')
        
        # Decode token and verify claims
        decoded = jwt.decode(
            company_token, 
            app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        assert decoded['sub'] == company_id
        assert decoded['user_type'] == 'company'
        assert 'exp' in decoded
        
        # Verify expiration date is set correctly (1 day in the future)
        now = datetime.utcnow()
        expiration = datetime.fromtimestamp(decoded['exp'])
        
        # Should be close to 1 day (allow a few seconds for test execution)
        time_diff = expiration - now
        assert time_diff < timedelta(days=1, seconds=5)
        assert time_diff > timedelta(hours=23, minutes=59)