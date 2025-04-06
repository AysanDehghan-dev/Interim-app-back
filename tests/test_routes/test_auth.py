import json
from datetime import datetime

import pytest
from bson import ObjectId


def test_register_user(client, db):
    # Test user registration data
    user_data = {
        "firstName": "New",
        "lastName": "User",
        "email": "new.user@example.com",
        "password": "password123",
        "confirmPassword": "password123",
    }

    # Register user
    response = client.post(
        "/api/auth/register/user",
        data=json.dumps(user_data),
        content_type="application/json",
    )

    # Check response
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "user" in data
    assert "token" in data
    assert data["user"]["firstName"] == "New"
    assert data["user"]["lastName"] == "User"
    assert data["user"]["email"] == "new.user@example.com"

    # Verify user was created in database
    user = db.users.find_one({"email": "new.user@example.com"})
    assert user is not None


def test_register_user_existing_email(client, test_user):
    # Test registration with existing email
    user_data = {
        "firstName": "Another",
        "lastName": "User",
        "email": test_user["email"],  # Use existing email
        "password": "password123",
        "confirmPassword": "password123",
    }

    # Try to register with existing email
    response = client.post(
        "/api/auth/register/user",
        data=json.dumps(user_data),
        content_type="application/json",
    )

    # Check response
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert "already registered" in data["error"]


def test_register_user_password_mismatch(client):
    # Test registration with mismatched passwords
    user_data = {
        "firstName": "Mismatched",
        "lastName": "Passwords",
        "email": "mismatched@example.com",
        "password": "password123",
        "confirmPassword": "different_password",  # Different from password
    }

    # Try to register with mismatched passwords
    response = client.post(
        "/api/auth/register/user",
        data=json.dumps(user_data),
        content_type="application/json",
    )

    # Check response
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_register_company(client, db):
    # Test company registration data
    company_data = {
        "name": "New Company",
        "industry": "Technology",
        "description": "A new test company",
        "email": "new.company@example.com",
        "password": "password123",
        "confirmPassword": "password123",
    }

    # Register company
    response = client.post(
        "/api/auth/register/company",
        data=json.dumps(company_data),
        content_type="application/json",
    )

    # Check response
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "company" in data
    assert "token" in data
    assert data["company"]["name"] == "New Company"
    assert data["company"]["email"] == "new.company@example.com"

    # Verify company was created in database
    company = db.companies.find_one({"email": "new.company@example.com"})
    assert company is not None


def test_login_user(client, app, db):
    # Create a user with known credentials
    from app.utils.security import hash_password

    user_data = {
        "first_name": "Login",
        "last_name": "Test",
        "email": "login.test@example.com",
        "password": hash_password("password123"),
        "created_at": datetime.utcnow(),  # Fix: Replace app.app_context().app.db.users.save with datetime
        "updated_at": datetime.utcnow(),  # Fix: Replace app.app_context().app.db.users.save with datetime
    }
    db.users.insert_one(user_data)

    # Login credentials
    login_data = {"email": "login.test@example.com", "password": "password123"}

    # Login user
    response = client.post(
        "/api/auth/login/user",
        data=json.dumps(login_data),
        content_type="application/json",
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "user" in data
    assert "token" in data
    assert data["user"]["email"] == "login.test@example.com"


def test_login_user_invalid_credentials(client):
    # Login with invalid credentials
    login_data = {"email": "invalid@example.com", "password": "wrongpassword"}

    # Try to login
    response = client.post(
        "/api/auth/login/user",
        data=json.dumps(login_data),
        content_type="application/json",
    )

    # Check response
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    assert "Invalid email or password" in data["error"]


def test_login_company(client, app, db):
    # Create a company with known credentials
    from app.utils.security import hash_password

    company_data = {
        "name": "Login Company",
        "industry": "Technology",
        "description": "A company for login testing",
        "email": "login.company@example.com",
        "password": hash_password("password123"),
        "created_at": datetime.utcnow(),  # Fix: Replace app.app_context().app.db.users.save with datetime
        "updated_at": datetime.utcnow(),  # Fix: Replace app.app_context().app.db.users.save with datetime
    }
    db.companies.insert_one(company_data)

    # Login credentials
    login_data = {"email": "login.company@example.com", "password": "password123"}

    # Login company
    response = client.post(
        "/api/auth/login/company",
        data=json.dumps(login_data),
        content_type="application/json",
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "company" in data
    assert "token" in data
    assert data["company"]["email"] == "login.company@example.com"
