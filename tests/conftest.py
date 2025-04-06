import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from datetime import datetime, timedelta

import mongomock
import pytest
from bson import ObjectId
from flask_jwt_extended import create_access_token

from app import create_app
from app.models.application import Application, ApplicationStatus
from app.models.company import Company
from app.models.job import Job, JobType
from app.models.user import User
from app.utils.security import hash_password


@pytest.fixture
def app():
    """Create and configure the Flask app for testing."""
    app = create_app()

    # Configure the app for testing
    app.config.update(
        {
            "TESTING": True,
            "JWT_SECRET_KEY": "test-secret-key",
        }
    )

    # Use mongomock instead of a real MongoDB connection
    mongo_client = mongomock.MongoClient()
    app.mongodb_client = mongo_client
    app.db = mongo_client["test_db"]

    # Make the db instance available to the application context
    with app.app_context():
        # Proceed with app setup
        yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Access to the test database."""
    return app.db


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": hash_password("password123"),
        "skills": ["Python", "Flask", "MongoDB"],
        "experience": [],
        "education": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    user_id = db.users.insert_one(user_data).inserted_id
    user_data["_id"] = user_id
    return user_data


@pytest.fixture
def test_company(db):
    """Create a test company."""
    company_data = {
        "name": "Test Company",
        "industry": "Technology",
        "description": "A test company for testing purposes",
        "email": "company@example.com",
        "password": hash_password("password123"),
        "jobs": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    company_id = db.companies.insert_one(company_data).inserted_id
    company_data["_id"] = company_id
    return company_data


@pytest.fixture
def test_job(db, test_company):
    """Create a test job."""
    job_data = {
        "title": "Test Job",
        "company_id": test_company["_id"],
        "description": "A test job for testing purposes",
        "requirements": ["Python", "Flask", "MongoDB"],
        "location": "Test City",
        "type": JobType.FULL_TIME,
        "salary": {"min": 50000, "max": 70000, "currency": "USD"},
        "applications": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "start_date": datetime.utcnow(),
    }
    job_id = db.jobs.insert_one(job_data).inserted_id
    job_data["_id"] = job_id

    # Update company with job reference
    db.companies.update_one({"_id": test_company["_id"]}, {"$push": {"jobs": job_id}})

    return job_data


@pytest.fixture
def test_application(db, test_user, test_job):
    """Create a test application."""
    application_data = {
        "user_id": test_user["_id"],
        "job_id": test_job["_id"],
        "status": ApplicationStatus.PENDING,
        "cover_letter": "I am interested in this position.",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    application_id = db.applications.insert_one(application_data).inserted_id
    application_data["_id"] = application_id

    # Update job with application reference
    db.jobs.update_one(
        {"_id": test_job["_id"]}, {"$push": {"applications": application_id}}
    )

    return application_data


@pytest.fixture
def user_token(app, test_user):
    """Create a JWT token for user authentication."""
    with app.app_context():
        return create_access_token(
            identity=str(test_user["_id"]),
            additional_claims={"user_type": "user"},
            expires_delta=timedelta(days=1),
        )


@pytest.fixture
def company_token(app, test_company):
    """Create a JWT token for company authentication."""
    with app.app_context():
        return create_access_token(
            identity=str(test_company["_id"]),
            additional_claims={"user_type": "company"},
            expires_delta=timedelta(days=1),
        )


@pytest.fixture
def auth_headers(user_token):
    """Headers with user JWT token."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def company_auth_headers(company_token):
    """Headers with company JWT token."""
    return {"Authorization": f"Bearer {company_token}"}
