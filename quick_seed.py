"""
Quick seeding script for development with minimal data
"""
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime

from dotenv import load_dotenv
from flask import Flask

# Load environment variables
load_dotenv()

from app.models.company import Company
from app.models.enums import JobType
from app.models.job import Job
from app.models.user import User
from config import get_config


def create_minimal_app():
    """Create minimal Flask app for database operations"""
    app = Flask(__name__)
    app_config = get_config()
    app.config.from_object(app_config)

    from urllib.parse import urlparse

    from pymongo import MongoClient

    mongodb_client = MongoClient(app.config["MONGODB_URI"])
    mongodb_client.admin.command("ping")

    parsed_uri = urlparse(app.config["MONGODB_URI"])
    db_name = parsed_uri.path.lstrip("/") or "interimapp"
    db = mongodb_client[db_name]

    app.mongodb_client = mongodb_client
    app.db = db

    return app


def quick_seed():
    """Create minimal data for testing"""
    app = create_minimal_app()

    with app.app_context():
        try:
            # Create one company
            company_id = Company.create(
                {
                    "name": "TestCorp",
                    "industry": "Technology",
                    "description": "Test company for development",
                    "email": "test@company.com",
                    "password": "password123",
                }
            )

            # Create one user
            user_id = User.create(
                {
                    "first_name": "Test",
                    "last_name": "User",
                    "email": "test@user.com",
                    "password": "password123",
                }
            )

            # Create one job
            job_id = Job.create(
                {
                    "title": "Test Developer",
                    "company_id": str(company_id),
                    "description": "Test job for development",
                    "requirements": ["Basic programming"],
                    "location": "Remote",
                    "type": JobType.FULL_TIME,
                }
            )

            print("✅ Quick seed completed!")
            print("🔐 Login with:")
            print("   Company: test@company.com / password123")
            print("   User: test@user.com / password123")

        except Exception as e:
            print(f"❌ Quick seed failed: {str(e)}")


if __name__ == "__main__":
    quick_seed()
