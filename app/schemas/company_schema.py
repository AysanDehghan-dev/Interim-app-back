from marshmallow import fields, validate, validates_schema
from marshmallow import ValidationError as MarshmallowValidationError

from app.schemas.base import BaseSchema, TimestampMixin, PhoneField, URLField


class CompanySchema(BaseSchema, TimestampMixin):
    """Schema for company data"""
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    industry = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    description = fields.Str(required=True, validate=validate.Length(min=10, max=2000))
    logo = fields.Str()
    website = URLField()
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, validate=validate.Length(min=6, max=128))
    phone = PhoneField()
    address = fields.Str(validate=validate.Length(max=200))
    city = fields.Str(validate=validate.Length(max=50))
    country = fields.Str(validate=validate.Length(max=50))
    jobs = fields.List(fields.Str(), dump_only=True)


class CompanyLoginSchema(BaseSchema):
    """Schema for company login"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))


class CompanyRegisterSchema(CompanySchema):
    """Schema for company registration"""
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    confirm_password = fields.Str(data_key="confirmPassword", required=True, load_only=True)
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        """Validate that passwords match"""
        if data.get("password") != data.get("confirm_password"):
            raise MarshmallowValidationError("Passwords must match", "confirm_password")


class CompanyUpdateSchema(BaseSchema):
    """Schema for updating company data (excludes password)"""
    name = fields.Str(validate=validate.Length(min=1, max=100))
    industry = fields.Str(validate=validate.Length(min=1, max=50))
    description = fields.Str(validate=validate.Length(min=10, max=2000))
    logo = fields.Str()
    website = URLField()
    phone = PhoneField()
    address = fields.Str(validate=validate.Length(max=200))
    city = fields.Str(validate=validate.Length(max=50))
    country = fields.Str(validate=validate.Length(max=50))