from marshmallow import Schema, fields, validate, post_load, pre_dump, validates_schema, ValidationError
from bson import ObjectId
from app.models.job import JobType

class SalarySchema(Schema):
    min = fields.Int(required=True)
    max = fields.Int(required=True)
    currency = fields.Str(required=True)
    
    @validates_schema
    def validate_salary(self, data, **kwargs):
        """Ensure max is greater than or equal to min"""
        if data['max'] < data['min']:
            raise ValidationError('Maximum salary must be greater than or equal to minimum salary')

class JobSchema(Schema):
    id = fields.Str()
    title = fields.Str(required=True, validate=validate.Length(min=1))
    companyId = fields.Str(attribute='company_id', required=True)
    description = fields.Str(required=True)
    requirements = fields.List(fields.Str(), required=True)
    location = fields.Str(required=True)
    type = fields.Str(required=True, validate=validate.OneOf([
        JobType.FULL_TIME, 
        JobType.PART_TIME, 
        JobType.CONTRACT, 
        JobType.TEMPORARY, 
        JobType.INTERNSHIP
    ]))
    salary = fields.Nested(SalarySchema)
    startDate = fields.DateTime(attribute='start_date')
    endDate = fields.DateTime(attribute='end_date')
    applications = fields.List(fields.Str(), dump_only=True)
    createdAt = fields.DateTime(attribute='created_at', dump_only=True)
    updatedAt = fields.DateTime(attribute='updated_at', dump_only=True)
    
    # Fields for job search and listing
    company = fields.Dict(dump_only=True)
    
    # Convert keys from snake_case to camelCase
    class Meta:
        ordered = True
    
    @pre_dump
    def prepare_data(self, data, **kwargs):
        """Convert ObjectId to string and prepare data for serialization"""
        if data and '_id' in data:
            data['id'] = str(data['_id'])
        
        # Convert company_id to string
        if data and 'company_id' in data and isinstance(data['company_id'], ObjectId):
            data['company_id'] = str(data['company_id'])
        
        # Convert application ObjectId list to string list
        if data and 'applications' in data:
            data['applications'] = [str(app_id) for app_id in data['applications']]
        
        return data
    
    @post_load
    def transform_keys(self, data, **kwargs):
        """Transform keys from camelCase to snake_case for MongoDB"""
        if 'company_id' not in data and 'companyId' in data:
            data['company_id'] = data.pop('companyId')
        if 'start_date' not in data and 'startDate' in data:
            data['start_date'] = data.pop('startDate')
        if 'end_date' not in data and 'endDate' in data:
            data['end_date'] = data.pop('endDate')
        return data


class JobSearchSchema(Schema):
    keyword = fields.Str()
    location = fields.Str()
    type = fields.Str(validate=validate.OneOf([
        JobType.FULL_TIME, 
        JobType.PART_TIME, 
        JobType.CONTRACT, 
        JobType.TEMPORARY, 
        JobType.INTERNSHIP
    ]))
    companyId = fields.Str(attribute='company_id')
    page = fields.Int(missing=1)
    limit = fields.Int(missing=10)
    
    # Convert keys from snake_case to camelCase
    class Meta:
        ordered = True