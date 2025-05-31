from marshmallow import fields, validate, validates_schema
from marshmallow import ValidationError as MarshmallowValidationError

from app.schemas.base import BaseSchema, TimestampMixin, PhoneField, ObjectIdField


class ExperienceSchema(BaseSchema):
    """Schema for user experience"""
    id = fields.Str(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    company = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    location = fields.Str(validate=validate.Length(max=100))
    start_date = fields.DateTime(data_key="startDate", required=True)
    end_date = fields.DateTime(data_key="endDate")
    current = fields.Bool(missing=False)
    description = fields.Str(validate=validate.Length(max=1000))
    
    @validates_schema
    def validate_dates(self, data, **kwargs):
        """Validate that end_date is after start_date"""
        if not data.get('current') and data.get('end_date') and data.get('start_date'):
            if data['end_date'] <= data['start_date']:
                raise MarshmallowValidationError("End date must be after start date")


class EducationSchema(BaseSchema):
    """Schema for user education"""
    id = fields.Str(dump_only=True)
    school = fields.Str(data_key="institution", required=True, validate=validate.Length(min=1, max=100))
    degree = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    field = fields.Str(data_key="field_of_study", required=True, validate=validate.Length(min=1, max=100))
    start_date = fields.DateTime(data_key="startDate", required=True)
    end_date = fields.DateTime(data_key="endDate")
    current = fields.Bool(missing=False)
    description = fields.Str(validate=validate.Length(max=500))
    
    @validates_schema
    def validate_dates(self, data, **kwargs):
        """Validate that end_date is after start_date"""
        if not data.get('current') and data.get('end_date') and data.get('start_date'):
            if data['end_date'] <= data['start_date']:
                raise MarshmallowValidationError("End date must be after start date")


class UserSchema(BaseSchema, TimestampMixin):
    """Schema for user data"""
    id = fields.Str(dump_only=True)
    first_name = fields.Str(
        data_key="firstName", 
        required=True, 
        validate=validate.Length(min=1, max=50)
    )
    last_name = fields.Str(
        data_key="lastName", 
        required=True, 
        validate=validate.Length(min=1, max=50)
    )
    email = fields.Email(required=True)
    password = fields.Str(
        load_only=True, 
        validate=validate.Length(min=6, max=128)
    )
    phone = PhoneField()
    address = fields.Str(validate=validate.Length(max=200))
    city = fields.Str(validate=validate.Length(max=50))
    country = fields.Str(validate=validate.Length(max=50))
    profile_picture = fields.Str(data_key="profilePicture")
    skills = fields.List(fields.Str(validate=validate.Length(max=50)), missing=list)
    experience = fields.List(fields.Nested(ExperienceSchema), missing=list)
    education = fields.List(fields.Nested(EducationSchema), missing=list)
    resume = fields.Str()


class UserLoginSchema(BaseSchema):
    """Schema for user login"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))


class UserRegisterSchema(UserSchema):
    """Schema for user registration"""
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    confirm_password = fields.Str(data_key="confirmPassword", required=True, load_only=True)
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        """Validate that passwords match"""
        if data.get("password") != data.get("confirm_password"):
            raise MarshmallowValidationError("Passwords must match", "confirm_password")


class UserUpdateSchema(BaseSchema):
    """Schema for updating user data (excludes password)"""
    first_name = fields.Str(data_key="firstName", validate=validate.Length(min=1, max=50))
    last_name = fields.Str(data_key="lastName", validate=validate.Length(min=1, max=50))
    phone = PhoneField()
    address = fields.Str(validate=validate.Length(max=200))
    city = fields.Str(validate=validate.Length(max=50))
    country = fields.Str(validate=validate.Length(max=50))
    profile_picture = fields.Str(data_key="profilePicture")
    skills = fields.List(fields.Str(validate=validate.Length(max=50)))