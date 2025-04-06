from datetime import datetime

from bson.objectid import ObjectId

from app.utils.db import (
    count_documents,
    find_by_id,
    find_many,
    find_one,
    insert_one,
    update_one,
)


class JobType:
    """Job type enumeration"""

    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    TEMPORARY = "TEMPORARY"
    INTERNSHIP = "INTERNSHIP"


class Job:
    """Job model class"""

    COLLECTION = "jobs"

    @staticmethod
    def create(job_data):
        """
        Create a new job
        """
        # Make sure company_id is stored as ObjectId
        if "company_id" in job_data and not isinstance(
            job_data["company_id"], ObjectId
        ):
            job_data["company_id"] = ObjectId(job_data["company_id"])

        # Initialize empty array for applications
        if "applications" not in job_data:
            job_data["applications"] = []

        # Add timestamps if not provided
        if "created_at" not in job_data:
            job_data["created_at"] = datetime.utcnow()
        if "updated_at" not in job_data:
            job_data["updated_at"] = datetime.utcnow()

        # Add start_date if not provided
        if "start_date" not in job_data:
            job_data["start_date"] = datetime.utcnow()

        job_id = insert_one(Job.COLLECTION, job_data)
        return job_id

    @staticmethod
    def find_by_id(job_id):
        """
        Find a job by ID
        """
        return find_by_id(Job.COLLECTION, job_id)

    @staticmethod
    def find_by_company(company_id, limit=0, skip=0):
        """
        Find jobs by company ID
        """
        query = {"company_id": ObjectId(company_id)}
        return find_many(Job.COLLECTION, query, limit=limit, skip=skip)

    @staticmethod
    def search(filters=None, limit=0, skip=0, sort=None):
        """
        Search jobs with filters
        """
        query = {}

        if not filters:
            filters = {}

        # Apply filters
        if "keyword" in filters and filters["keyword"]:
            keyword = filters["keyword"]
            query["$or"] = [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"description": {"$regex": keyword, "$options": "i"}},
                {"requirements": {"$regex": keyword, "$options": "i"}},
            ]

        if "location" in filters and filters["location"]:
            query["location"] = {"$regex": filters["location"], "$options": "i"}

        if "type" in filters and filters["type"]:
            query["type"] = filters["type"]

        if "company_id" in filters and filters["company_id"]:
            query["company_id"] = ObjectId(filters["company_id"])

        # Default sort by creation date (newest first)
        if not sort:
            sort = [("created_at", -1)]

        return find_many(Job.COLLECTION, query, sort=sort, limit=limit, skip=skip)

    @staticmethod
    def count(filters=None):
        """
        Count jobs matching filters
        """
        query = {}

        if not filters:
            filters = {}

        # Apply filters (same as in search method)
        if "keyword" in filters and filters["keyword"]:
            keyword = filters["keyword"]
            query["$or"] = [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"description": {"$regex": keyword, "$options": "i"}},
                {"requirements": {"$regex": keyword, "$options": "i"}},
            ]

        if "location" in filters and filters["location"]:
            query["location"] = {"$regex": filters["location"], "$options": "i"}

        if "type" in filters and filters["type"]:
            query["type"] = filters["type"]

        if "company_id" in filters and filters["company_id"]:
            query["company_id"] = ObjectId(filters["company_id"])

        return count_documents(Job.COLLECTION, query)

    @staticmethod
    def update(job_id, job_data):
        """
        Update a job
        """
        # Make sure company_id is stored as ObjectId if provided
        if "company_id" in job_data and not isinstance(
            job_data["company_id"], ObjectId
        ):
            job_data["company_id"] = ObjectId(job_data["company_id"])

        # Update the updated_at timestamp
        job_data["updated_at"] = datetime.utcnow()

        return update_one(Job.COLLECTION, job_id, job_data)

    @staticmethod
    def add_application(job_id, application_id):
        """
        Add application reference to job
        """
        job = Job.find_by_id(job_id)

        if not job:
            return False

        applications = job.get("applications", [])

        # Add application_id as string if it's not already in the list
        if str(application_id) not in [str(a) for a in applications]:
            applications.append(application_id)
            update_one(Job.COLLECTION, job_id, {"applications": applications})
            return True

        return False
