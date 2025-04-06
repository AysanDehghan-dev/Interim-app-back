from app.utils.db import insert_one, find_one, update_one, find_by_id, find_many
from app.utils.security import hash_password, verify_password
from bson.objectid import ObjectId


class Company:
    """Company model class"""

    COLLECTION = "companies"

    @staticmethod
    def create(company_data):
        """
        Create a new company
        """
        # Hash the password before storing
        if "password" in company_data:
            company_data["password"] = hash_password(company_data["password"])

        # Initialize empty array for jobs
        if "jobs" not in company_data:
            company_data["jobs"] = []

        company_id = insert_one(Company.COLLECTION, company_data)
        return company_id

    @staticmethod
    def find_by_email(email):
        """
        Find a company by email
        """
        return find_one(Company.COLLECTION, {"email": email})

    @staticmethod
    def find_by_id(company_id):
        """
        Find a company by ID
        """
        return find_by_id(Company.COLLECTION, company_id)

    @staticmethod
    def find_all(limit=0, skip=0):
        """
        Find all companies
        """
        # Don't return the password field
        projection = {"password": 0}
        return find_many(Company.COLLECTION, {}, limit=limit, skip=skip)

    @staticmethod
    def update(company_id, company_data):
        """
        Update a company
        """
        # Don't allow updating the password through this method
        if "password" in company_data:
            del company_data["password"]

        return update_one(Company.COLLECTION, company_id, company_data)

    @staticmethod
    def update_password(company_id, new_password):
        """
        Update company's password
        """
        hashed_password = hash_password(new_password)
        return update_one(Company.COLLECTION, company_id, {"password": hashed_password})

    @staticmethod
    def authenticate(email, password):
        """
        Authenticate a company with email and password
        """
        company = Company.find_by_email(email)

        if not company or "password" not in company:
            return None

        if verify_password(password, company["password"]):
            return company

        return None

    @staticmethod
    def add_job(company_id, job_id):
        """
        Add job reference to company
        """
        company = Company.find_by_id(company_id)

        if not company:
            return False

        jobs = company.get("jobs", [])

        # Add job_id as string if it's not already in the list
        if str(job_id) not in [str(j) for j in jobs]:
            jobs.append(job_id)
            update_one(Company.COLLECTION, company_id, {"jobs": jobs})
            return True

        return False
