from marshmallow import fields, validate, validates_schema
from marshmallow import ValidationError as MarshmallowValidationError

from app.schemas.base import BaseSchema, TimestampMixin, EnumField, ObjectIdField, PaginationSchema
from app.models.enums import JobType


class SalarySchema(BaseSchema):
    """Schema for salary information"""
    min_salary = fields.Int(data_key="min", required=True, validate=validate.Range(min=0))
    max_salary = fields.Int(data_key="max", required=True, validate=validate.Range(min=0))
    currency = fields.Str(required=True, validate=validate.Length(equal=3))  # USD, EUR, etc.
    
    @validates_schema
    def validate_salary_range(self, data, **kwargs):
        """Ensure max is greater than or equal to min"""
        if data.get("max_salary", 0) < data.get("min_salary", 0):
            raise MarshmallowValidationError("Maximum salary must be greater than or equal to minimum salary")


class JobSchema(BaseSchema, TimestampMixin):
    """Schema for job data"""
    id = fields.Str(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    company_id = ObjectIdField(data_key="companyId", required=True)
    description = fields.Str(required=True, validate=validate.Length(min=10, max=5000))
    requirements = fields.List(
        fields.Str(validate=validate.Length(min=1, max=200)), 
        required=True,
        validate=validate.Length(min=1, max=20)
    )
    location = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    type = EnumField(JobType, required=True)
    salary = fields.Nested(SalarySchema)
    start_date = fields.DateTime(data_key="startDate")
    end_date = fields.DateTime(data_key="endDate")
    applications = fields.List(fields.Str(), dump_only=True)
    
    # Populated fields for job listings
    company = fields.Dict(dump_only=True)
    
    @validates_schema
    def validate_dates(self, data, **kwargs):
        """Validate that end_date is after start_date"""
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] <= data['start_date']:
                raise MarshmallowValidationError("End date must be after start date")


class JobCreateSchema(BaseSchema):
    """Schema for creating jobs (simplified)"""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=True, validate=validate.Length(min=10, max=5000))
    requirements = fields.List(
        fields.Str(validate=validate.Length(min=1, max=200)), 
        required=True,
        validate=validate.Length(min=1, max=20)
    )
    location = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    type = EnumField(JobType, required=True)
    salary = fields.Nested(SalarySchema)
    start_date = fields.DateTime(data_key="startDate")
    end_date = fields.DateTime(data_key="endDate")


class JobUpdateSchema(BaseSchema):
    """Schema for updating jobs"""
    title = fields.Str(validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(min=10, max=5000))
    requirements = fields.List(
        fields.Str(validate=validate.Length(min=1, max=200)), 
        validate=validate.Length(min=1, max=20)
    )
    location = fields.Str(validate=validate.Length(min=1, max=100))
    type = EnumField(JobType)
    salary = fields.Nested(SalarySchema)
    start_date = fields.DateTime(data_key="startDate")
    end_date = fields.DateTime(data_key="endDate")


class JobSearchSchema(PaginationSchema):
    """Schema for job search with filters"""
    keyword = fields.Str(validate=validate.Length(max=100))
    location = fields.Str(validate=validate.Length(max=100))
    type = EnumField(JobType)
    company_id = ObjectIdField(data_key="companyId")
    min_salary = fields.Int(data_key="minSalary", validate=validate.Range(min=0))
    max_salary = fields.Int(data_key="maxSalary", validate=validate.Range(min=0))
    
    @validates_schema
    def validate_salary_range(self, data, **kwargs):
        """Validate salary range if both provided"""
        min_sal = data.get("min_salary")
        max_sal = data.get("max_salary")
        if min_sal is not None and max_sal is not None and max_sal < min_sal:
            raise MarshmallowValidationError("Maximum salary must be greater than minimum salary")