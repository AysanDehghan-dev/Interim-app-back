from marshmallow import Schema, fields, validate, post_load, pre_dump, validates_schema, ValidationError
from bson import ObjectId

class ExperienceSchema(Schema):
    id = fields.Str()
    title = fields.Str(required=True)
    company = fields.Str(required=True)
    location = fields.Str()
    startDate = fields.DateTime(attribute='start_date', required=True)
    endDate = fields.DateTime(attribute='end_date')
    current = fields.Bool(default=False)
    description = fields.Str()
    
    # Convert keys from snake_case to camelCase
    class Meta:
        ordered = True

class EducationSchema(Schema):
    id = fields.Str()
    institution = fields.Str(required=True)
    degree = fields.Str(required=True)
    field = fields.Str(required=True)
    startDate = fields.DateTime(attribute='start_date', required=True)
    endDate = fields.DateTime(attribute='end_date')
    current = fields.Bool(default=False)
    description = fields.Str()
    
    # Convert keys from snake_case to camelCase
    class Meta:
        ordered = True

class UserSchema(Schema):
    id = fields.Str()
    firstName = fields.Str(attribute='first_name', required=True, validate=validate.Length(min=1))
    lastName = fields.Str(attribute='last_name', required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, validate=validate.Length(min=6))
    phone = fields.Str()
    address = fields.Str()
    city = fields.Str()
    country = fields.Str()
    profilePicture = fields.Str(attribute='profile_picture')
    skills = fields.List(fields.Str(), default=[])
    experience = fields.List(fields.Nested(ExperienceSchema), default=[])
    education = fields.List(fields.Nested(EducationSchema), default=[])
    resume = fields.Str()
    createdAt = fields.DateTime(attribute='created_at', dump_only=True)
    updatedAt = fields.DateTime(attribute='updated_at', dump_only=True)
    
    # Convert keys from snake_case to camelCase
    class Meta:
        ordered = True
    
    @pre_dump
    def prepare_data(self, data, **kwargs):
        """Convert ObjectId to string and prepare data for serialization"""
        if data and '_id' in data:
            data['id'] = str(data['_id'])
        return data
    
    @post_load
    def transform_keys(self, data, **kwargs):
        """Transform keys from camelCase to snake_case for MongoDB"""
        if 'first_name' not in data and 'firstName' in data:
            data['first_name'] = data.pop('firstName')
        if 'last_name' not in data and 'lastName' in data:
            data['last_name'] = data.pop('lastName')
        if 'profile_picture' not in data and 'profilePicture' in data:
            data['profile_picture'] = data.pop('profilePicture')
        return data


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    
    class Meta:
        ordered = True

class UserRegisterSchema(UserSchema):
    password = fields.Str(required=True, validate=validate.Length(min=6))
    confirmPassword = fields.Str(required=True)
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        """Validate that password and confirmPassword match"""
        if data.get('password') != data.get('confirmPassword'):
            raise ValidationError('Passwords must match', 'confirmPassword')
    
    class Meta:
        ordered = True