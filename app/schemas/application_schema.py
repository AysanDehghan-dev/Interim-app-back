from marshmallow import fields, validate

from app.models.enums import ApplicationStatus
from app.schemas.base import BaseSchema, EnumField, ObjectIdField, PaginationSchema, TimestampMixin


class ApplicationSchema(BaseSchema, TimestampMixin):
    """Schema for job application data"""

    id = fields.Str(dump_only=True)
    job_id = ObjectIdField(data_key="jobId", required=True)
    user_id = ObjectIdField(data_key="userId", required=True)
    status = EnumField(ApplicationStatus, missing=ApplicationStatus.PENDING)
    cover_letter = fields.Str(
        data_key="coverLetter", validate=validate.Length(max=2000)
    )
    resume = fields.Str()

    # Populated fields for application listings
    job = fields.Dict(dump_only=True)
    user = fields.Dict(dump_only=True)


class ApplicationCreateSchema(BaseSchema):
    """Schema for creating applications"""

    job_id = ObjectIdField(data_key="jobId", required=True)
    cover_letter = fields.Str(
        data_key="coverLetter", validate=validate.Length(max=2000)
    )
    resume = fields.Str()


class ApplicationStatusUpdateSchema(BaseSchema):
    """Schema for updating application status"""

    status = EnumField(ApplicationStatus, required=True)


class ApplicationSearchSchema(PaginationSchema):
    """Schema for searching applications"""

    status = EnumField(ApplicationStatus)
    job_id = ObjectIdField(data_key="jobId")
    user_id = ObjectIdField(data_key="userId")
