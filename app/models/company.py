from app.models.base import BaseModel
from app.models.exceptions import ValidationError
from app.utils.db import find_many, find_one, insert_one, update_one
from app.utils.security import hash_password, verify_password


class Company(BaseModel):
    """Company model class"""

    COLLECTION = "companies"

    @classmethod
    def create(cls, company_data):
        """Create a new company"""
        # Validate required fields
        if not company_data.get("email"):
            raise ValidationError("Email is required")
        if not company_data.get("password"):
            raise ValidationError("Password is required")
        if not company_data.get("name"):
            raise ValidationError("Company name is required")

        # Validate email format
        company_data["email"] = cls._validate_email(company_data["email"])

        # Check if email already exists
        if cls.find_by_email(company_data["email"]):
            raise ValidationError("Email already exists")

        # Hash password
        company_data["password"] = hash_password(company_data["password"])

        # Initialize empty jobs array
        company_data.setdefault("jobs", [])

        # Add timestamps
        cls._add_timestamps(company_data)

        return insert_one(cls.COLLECTION, company_data)

    @classmethod
    def find_by_email(cls, email):
        """Find company by email"""
        if not email:
            return None
        return find_one(cls.COLLECTION, {"email": email.lower().strip()})

    @classmethod
    def find_all(cls, limit=0, skip=0):
        """Find all companies (without passwords)"""
        projection = {"password": 0}
        return find_many(
            cls.COLLECTION, {}, projection=projection, limit=limit, skip=skip
        )

    @classmethod
    def update(cls, company_id, company_data):
        """Update company"""
        # Remove password from regular updates
        if "password" in company_data:
            del company_data["password"]

        # Validate email if provided
        if "email" in company_data:
            company_data["email"] = cls._validate_email(company_data["email"])

            # Check if email is already taken
            existing = cls.find_by_email(company_data["email"])
            if existing and str(existing["_id"]) != str(company_id):
                raise ValidationError("Email already exists")

        # Add update timestamp
        cls._add_timestamps(company_data, is_update=True)

        return update_one(cls.COLLECTION, company_id, company_data)

    @classmethod
    def update_password(cls, company_id, new_password):
        """Update company password"""
        if not new_password:
            raise ValidationError("Password cannot be empty")

        hashed_password = hash_password(new_password)
        data = {"password": hashed_password}
        cls._add_timestamps(data, is_update=True)

        return update_one(cls.COLLECTION, company_id, data)

    @classmethod
    def authenticate(cls, email, password):
        """Authenticate company"""
        if not email or not password:
            return None

        company = cls.find_by_email(email)
        if not company or "password" not in company:
            return None

        if verify_password(password, company["password"]):
            return company

        return None

    @classmethod
    def add_job(cls, company_id, job_id):
        """Add job reference to company"""
        company = cls.find_by_id(company_id)
        if not company:
            raise ValidationError("Company not found")

        jobs = company.get("jobs", [])

        # Add job_id if not already present
        job_id_str = str(job_id)
        if job_id_str not in [str(j) for j in jobs]:
            jobs.append(job_id)

            update_data = {"jobs": jobs}
            cls._add_timestamps(update_data, is_update=True)

            update_one(cls.COLLECTION, company_id, update_data)
            return True

        return False
