import pytest
from bson import ObjectId

from app.models.application import Application, ApplicationStatus


def test_create_application(app, test_user, test_job, db):
    with app.app_context():
        # Test application data
        application_data = {
            "user_id": test_user["_id"],
            "job_id": test_job["_id"],
            "cover_letter": "I am interested in this position.",
        }

        # Create application
        application_id = Application.create(application_data)
        assert application_id is not None

        # Verify application was created in database
        application = db.applications.find_one({"_id": application_id})
        assert application is not None
        assert str(application["user_id"]) == str(test_user["_id"])
        assert str(application["job_id"]) == str(test_job["_id"])
        assert application["cover_letter"] == "I am interested in this position."

        # Verify default fields were initialized
        assert application["status"] == ApplicationStatus.PENDING
        assert "created_at" in application
        assert "updated_at" in application


def test_find_by_id(app, test_application):
    with app.app_context():
        # Find application by ID
        application = Application.find_by_id(test_application["_id"])
        assert application is not None
        assert str(application["user_id"]) == str(test_application["user_id"])
        assert str(application["job_id"]) == str(test_application["job_id"])

        # Test with non-existent ID
        non_existent = Application.find_by_id(ObjectId())
        assert non_existent is None


def test_find_by_user(app, test_user, test_job, test_application, db):
    with app.app_context():
        # Add another application for the same user
        another_application_data = {
            "user_id": test_user["_id"],
            "job_id": test_job["_id"],
            "status": ApplicationStatus.REVIEWING,
            "cover_letter": "Another application",
            "created_at": test_application["created_at"],
            "updated_at": test_application["updated_at"],
        }
        db.applications.insert_one(another_application_data)

        # Find applications by user
        applications = Application.find_by_user(test_user["_id"])
        assert len(applications) >= 2

        # Test with pagination
        limited_applications = Application.find_by_user(test_user["_id"], limit=1)
        assert len(limited_applications) == 1


def test_find_by_job(app, test_user, test_job, test_application, db):
    with app.app_context():
        # Add another application for the same job
        another_user_id = ObjectId()
        another_application_data = {
            "user_id": another_user_id,
            "job_id": test_job["_id"],
            "status": ApplicationStatus.PENDING,
            "cover_letter": "Application from another user",
            "created_at": test_application["created_at"],
            "updated_at": test_application["updated_at"],
        }
        db.applications.insert_one(another_application_data)

        # Find applications by job
        applications = Application.find_by_job(test_job["_id"])
        assert len(applications) >= 2

        # Test with pagination
        limited_applications = Application.find_by_job(test_job["_id"], limit=1)
        assert len(limited_applications) == 1


def test_find_by_user_and_job(app, test_user, test_job, test_application):
    with app.app_context():
        # Find application by user and job
        application = Application.find_by_user_and_job(
            test_user["_id"], test_job["_id"]
        )
        assert application is not None
        assert str(application["user_id"]) == str(test_user["_id"])
        assert str(application["job_id"]) == str(test_job["_id"])

        # Test with non-existent user
        non_existent = Application.find_by_user_and_job(ObjectId(), test_job["_id"])
        assert non_existent is None

        # Test with non-existent job
        non_existent = Application.find_by_user_and_job(test_user["_id"], ObjectId())
        assert non_existent is None


def test_update_status(app, test_application):
    with app.app_context():
        # Update status to REVIEWING
        result = Application.update_status(
            test_application["_id"], ApplicationStatus.REVIEWING
        )
        assert result is True

        # Verify status was updated
        updated_application = Application.find_by_id(test_application["_id"])
        assert updated_application["status"] == ApplicationStatus.REVIEWING

        # Test all valid statuses
        for status in [
            ApplicationStatus.PENDING,
            ApplicationStatus.REVIEWING,
            ApplicationStatus.INTERVIEW,
            ApplicationStatus.REJECTED,
            ApplicationStatus.ACCEPTED,
        ]:
            result = Application.update_status(test_application["_id"], status)
            assert result is True
            updated = Application.find_by_id(test_application["_id"])
            assert updated["status"] == status

        # Test with invalid status
        result = Application.update_status(test_application["_id"], "INVALID_STATUS")
        assert result is False

        # Test with non-existent ID
        result = Application.update_status(ObjectId(), ApplicationStatus.REVIEWING)
        assert result is False
