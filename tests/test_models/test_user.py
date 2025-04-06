import pytest
from bson import ObjectId
from datetime import datetime

from app.models.user import User


def test_create_user(app, db):
    with app.app_context():
        # Test user data
        user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "secure_password123",
        }

        # Create user
        user_id = User.create(user_data)
        assert user_id is not None

        # Verify user was created in database
        user = db.users.find_one({"_id": user_id})
        assert user is not None
        assert user["first_name"] == "John"
        assert user["last_name"] == "Doe"
        assert user["email"] == "john.doe@example.com"
        assert user["password"] != "secure_password123"  # Password should be hashed

        # Verify default fields were initialized
        assert isinstance(user["skills"], list)
        assert isinstance(user["experience"], list)
        assert isinstance(user["education"], list)


def test_find_by_email(app, test_user):
    with app.app_context():
        # Find user by email
        user = User.find_by_email(test_user["email"])
        assert user is not None
        assert str(user["_id"]) == str(test_user["_id"])

        # Test with non-existent email
        non_existent = User.find_by_email("non.existent@example.com")
        assert non_existent is None


def test_find_by_id(app, test_user):
    with app.app_context():
        # Find user by ID
        user = User.find_by_id(test_user["_id"])
        assert user is not None
        assert user["email"] == test_user["email"]

        # Test with non-existent ID
        non_existent = User.find_by_id(ObjectId())
        assert non_existent is None


def test_update_user(app, test_user):
    with app.app_context():
        # Update data
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "123-456-7890",
        }

        # Update user
        result = User.update(test_user["_id"], update_data)
        assert result > 0

        # Verify user was updated
        updated_user = User.find_by_id(test_user["_id"])
        assert updated_user["first_name"] == "Updated"
        assert updated_user["last_name"] == "Name"
        assert updated_user["phone"] == "123-456-7890"

        # Password shouldn't be updatable through this method
        update_with_password = {"password": "new_password"}
        User.update(test_user["_id"], update_with_password)
        updated_user = User.find_by_id(test_user["_id"])
        # The password field shouldn't be changed
        assert updated_user["password"] == test_user["password"]


def test_update_password(app, test_user, db):
    with app.app_context():
        # Original password hash
        original_password = test_user["password"]

        # Update password
        User.update_password(test_user["_id"], "new_secure_password")

        # Verify password was updated
        updated_user = db.users.find_one({"_id": test_user["_id"]})
        assert updated_user["password"] != original_password


def test_authenticate(app, test_user):
    with app.app_context():
        # Set up a user with known credentials
        email = "auth.test@example.com"
        password = "test_password"

        user_data = {
            "first_name": "Auth",
            "last_name": "Test",
            "email": email,
            "password": password,
        }

        User.create(user_data)

        # Test successful authentication
        auth_user = User.authenticate(email, password)
        assert auth_user is not None
        assert auth_user["email"] == email

        # Test failed authentication with wrong password
        failed_auth = User.authenticate(email, "wrong_password")
        assert failed_auth is None

        # Test failed authentication with non-existent email
        failed_auth = User.authenticate("non.existent@example.com", password)
        assert failed_auth is None


def test_add_experience(app, test_user):
    with app.app_context():
        # Experience data
        experience = {
            "title": "Software Developer",
            "company": "Tech Company",
            "location": "Remote",
            "start_date": datetime(2020, 1, 1),
        }

        # Add experience
        experience_id = User.add_experience(test_user["_id"], experience)
        assert experience_id is not None

        # Verify experience was added
        updated_user = User.find_by_id(test_user["_id"])
        assert len(updated_user["experience"]) == 1
        added_exp = updated_user["experience"][0]
        assert added_exp["id"] == experience_id
        assert added_exp["title"] == experience["title"]
        assert added_exp["company"] == experience["company"]
        assert "created_at" in added_exp
        assert "updated_at" in added_exp


def test_add_education(app, test_user):
    with app.app_context():
        # Education data
        education = {
            "institution": "University",
            "degree": "Bachelor",
            "field": "Computer Science",
            "start_date": datetime(2015, 9, 1),
        }

        # Add education
        education_id = User.add_education(test_user["_id"], education)
        assert education_id is not None

        # Verify education was added
        updated_user = User.find_by_id(test_user["_id"])
        assert len(updated_user["education"]) == 1
        added_edu = updated_user["education"][0]
        assert added_edu["id"] == education_id
        assert added_edu["institution"] == education["institution"]
        assert added_edu["degree"] == education["degree"]
        assert "created_at" in added_edu
        assert "updated_at" in added_edu
