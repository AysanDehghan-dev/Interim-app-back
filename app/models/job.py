from datetime import datetime

from app.models.base import BaseModel
from app.models.enums import JobType
from app.models.exceptions import ValidationError
from app.utils.db import count_documents, find_many, insert_one, update_one


class Job(BaseModel):
    """Job model class"""

    COLLECTION = "jobs"

    @classmethod
    def _build_search_query(cls, filters):
        """Build MongoDB query from filters (reusable for search and count)"""
        query = {}

        if not filters:
            return query

        # Keyword search
        if filters.get("keyword"):
            keyword = filters["keyword"]
            query["$or"] = [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"description": {"$regex": keyword, "$options": "i"}},
                {"requirements": {"$regex": keyword, "$options": "i"}},
            ]

        # Location filter
        if filters.get("location"):
            query["location"] = {"$regex": filters["location"], "$options": "i"}

        # Job type filter
        if filters.get("type"):
            if JobType.is_valid(filters["type"]):
                query["type"] = filters["type"]

        # Company filter
        if filters.get("company_id"):
            query["company_id"] = cls._validate_object_id(
                filters["company_id"], "company_id"
            )

        # Salary range filter
        if filters.get("min_salary"):
            query.setdefault("salary", {})["$gte"] = int(filters["min_salary"])

        if filters.get("max_salary"):
            query.setdefault("salary", {})["$lte"] = int(filters["max_salary"])

        return query

    @classmethod
    def create(cls, job_data):
        """Create a new job"""
        # Validate required fields
        if not job_data.get("title"):
            raise ValidationError("Job title is required")
        if not job_data.get("description"):
            raise ValidationError("Job description is required")
        if not job_data.get("company_id"):
            raise ValidationError("Company ID is required")

        # Validate company_id
        job_data["company_id"] = cls._validate_object_id(
            job_data["company_id"], "company_id"
        )

        # Validate job type if provided
        if job_data.get("type") and not JobType.is_valid(job_data["type"]):
            raise ValidationError(
                f"Invalid job type. Must be one of: {', '.join(JobType.get_all())}"
            )

        # Set defaults
        job_data.setdefault("applications", [])
        job_data.setdefault("type", JobType.FULL_TIME)

        # Set start_date if not provided
        if "start_date" not in job_data:
            job_data["start_date"] = datetime.utcnow()

        # Add timestamps
        cls._add_timestamps(job_data)

        return insert_one(cls.COLLECTION, job_data)

    @classmethod
    def find_by_company(cls, company_id, limit=0, skip=0):
        """Find jobs by company"""
        company_id = cls._validate_object_id(company_id, "company_id")
        query = {"company_id": company_id}
        sort = [("created_at", -1)]

        return find_many(cls.COLLECTION, query, sort=sort, limit=limit, skip=skip)

    @classmethod
    def search(cls, filters=None, limit=0, skip=0, sort=None):
        """Search jobs with filters"""
        query = cls._build_search_query(filters)

        # Default sort by creation date (newest first)
        if not sort:
            sort = [("created_at", -1)]

        return find_many(cls.COLLECTION, query, sort=sort, limit=limit, skip=skip)

    @classmethod
    def count(cls, filters=None):
        """Count jobs matching filters"""
        query = cls._build_search_query(filters)
        return count_documents(cls.COLLECTION, query)

    @classmethod
    def update(cls, job_id, job_data):
        """Update a job"""
        # Validate company_id if provided
        if "company_id" in job_data:
            job_data["company_id"] = cls._validate_object_id(
                job_data["company_id"], "company_id"
            )

        # Validate job type if provided
        if job_data.get("type") and not JobType.is_valid(job_data["type"]):
            raise ValidationError(
                f"Invalid job type. Must be one of: {', '.join(JobType.get_all())}"
            )

        # Add update timestamp
        cls._add_timestamps(job_data, is_update=True)

        return update_one(cls.COLLECTION, job_id, job_data)

    @classmethod
    def add_application(cls, job_id, application_id):
        """Add application reference to job"""
        job = cls.find_by_id(job_id)
        if not job:
            raise ValidationError("Job not found")

        applications = job.get("applications", [])

        # Add application_id if not already present
        application_id_str = str(application_id)
        if application_id_str not in [str(a) for a in applications]:
            applications.append(application_id)

            update_data = {"applications": applications}
            cls._add_timestamps(update_data, is_update=True)

            update_one(cls.COLLECTION, job_id, update_data)
            return True

        return False
