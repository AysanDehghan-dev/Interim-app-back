from .application_schema import (
    ApplicationCreateSchema,
    ApplicationSchema,
    ApplicationSearchSchema,
    ApplicationStatusUpdateSchema,
)
from .base import BaseSchema, PaginationSchema
from .company_schema import (
    CompanyLoginSchema,
    CompanyRegisterSchema,
    CompanySchema,
    CompanyUpdateSchema,
)
from .job_schema import (
    JobCreateSchema,
    JobSchema,
    JobSearchSchema,
    JobUpdateSchema,
    SalarySchema,
)
from .user_schema import (
    EducationSchema,
    ExperienceSchema,
    UserLoginSchema,
    UserRegisterSchema,
    UserSchema,
    UserUpdateSchema,
)

__all__ = [
    # Base
    "BaseSchema",
    "PaginationSchema",
    # User schemas
    "UserSchema",
    "UserLoginSchema",
    "UserRegisterSchema",
    "UserUpdateSchema",
    "ExperienceSchema",
    "EducationSchema",
    # Company schemas
    "CompanySchema",
    "CompanyLoginSchema",
    "CompanyRegisterSchema",
    "CompanyUpdateSchema",
    # Job schemas
    "JobSchema",
    "JobCreateSchema",
    "JobUpdateSchema",
    "JobSearchSchema",
    "SalarySchema",
    # Application schemas
    "ApplicationSchema",
    "ApplicationCreateSchema",
    "ApplicationStatusUpdateSchema",
    "ApplicationSearchSchema",
]
