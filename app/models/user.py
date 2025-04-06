from bson.objectid import ObjectId

from app.utils.db import find_by_id, find_one, insert_one, update_one
from app.utils.security import hash_password, verify_password


class User:
    """User model class"""

    COLLECTION = "users"

    @staticmethod
    def create(user_data):
        """
        Create a new user
        """
        # Hash the password before storing
        if "password" in user_data:
            user_data["password"] = hash_password(user_data["password"])

        # Initialize empty arrays for skills, experience and education if not provided
        if "skills" not in user_data:
            user_data["skills"] = []
        if "experience" not in user_data:
            user_data["experience"] = []
        if "education" not in user_data:
            user_data["education"] = []

        user_id = insert_one(User.COLLECTION, user_data)
        return user_id

    @staticmethod
    def find_by_email(email):
        """
        Find a user by email
        """
        return find_one(User.COLLECTION, {"email": email})

    @staticmethod
    def find_by_id(user_id):
        """
        Find a user by ID
        """
        return find_by_id(User.COLLECTION, user_id)

    @staticmethod
    def update(user_id, user_data):
        """
        Update a user
        """
        # Don't allow updating the password through this method
        if "password" in user_data:
            del user_data["password"]

        return update_one(User.COLLECTION, user_id, user_data)

    @staticmethod
    def update_password(user_id, new_password):
        """
        Update user's password
        """
        hashed_password = hash_password(new_password)
        return update_one(User.COLLECTION, user_id, {"password": hashed_password})

    @staticmethod
    def authenticate(email, password):
        """
        Authenticate a user with email and password
        """
        user = User.find_by_email(email)

        if not user or "password" not in user:
            return None

        if verify_password(password, user["password"]):
            return user

        return None

    @staticmethod
    def add_experience(user_id, experience_data):
        """
        Add experience to user
        """
        user = User.find_by_id(user_id)

        if not user:
            return None

        # Generate an ObjectId for the experience
        experience_data["id"] = str(ObjectId())

        # Add created_at and updated_at timestamps
        from datetime import datetime

        experience_data["created_at"] = datetime.utcnow()
        experience_data["updated_at"] = datetime.utcnow()

        experiences = user.get("experience", [])
        experiences.append(experience_data)

        update_one(User.COLLECTION, user_id, {"experience": experiences})
        return experience_data["id"]

    @staticmethod
    def add_education(user_id, education_data):
        """
        Add education to user
        """
        user = User.find_by_id(user_id)

        if not user:
            return None

        # Generate an ObjectId for the education
        education_data["id"] = str(ObjectId())

        # Add created_at and updated_at timestamps
        from datetime import datetime

        education_data["created_at"] = datetime.utcnow()
        education_data["updated_at"] = datetime.utcnow()

        education = user.get("education", [])
        education.append(education_data)

        update_one(User.COLLECTION, user_id, {"education": education})
        return education_data["id"]
