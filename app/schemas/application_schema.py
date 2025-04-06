from marshmallow import Schema, fields, validate, post_load, pre_dump
from bson import ObjectId
from app.models.application import ApplicationStatus

class ApplicationSchema(Schema):
    id = fields.Str()
    jobId = fields.Str(attribute='job_id', required=True)
    userId = fields.Str(attribute='user_id', required=True)
    status = fields.Str(validate=validate.OneOf([
        ApplicationStatus.PENDING,
        ApplicationStatus.REVIEWING,
        ApplicationStatus.INTERVIEW,
        ApplicationStatus.REJECTED,
        ApplicationStatus.ACCEPTED
    ]), default=ApplicationStatus.PENDING)
    coverLetter = fields.Str(attribute='cover_letter')
    resume = fields.Str()
    createdAt = fields.DateTime(attribute='created_at', dump_only=True)
    updatedAt = fields.DateTime(attribute='updated_at', dump_only=True)
    
    # Fields for application listing (populated from related documents)
    job = fields.Dict(dump_only=True)
    user = fields.Dict(dump_only=True)
    
    # Convert keys from snake_case to camelCase
    class Meta:
        ordered = True
    
    @pre_dump
    def prepare_data(self, data, **kwargs):
        """Convert ObjectId to string and prepare data for serialization"""
        if data and '_id' in data:
            data['id'] = str(data['_id'])
        
        # Convert job_id to string
        if data and 'job_id' in data and isinstance(data['job_id'], ObjectId):
            data['job_id'] = str(data['job_id'])
        
        # Convert user_id to string
        if data and 'user_id' in data and isinstance(data['user_id'], ObjectId):
            data['user_id'] = str(data['user_id'])
        
        return data
    
    @post_load
    def transform_keys(self, data, **kwargs):
        """Transform keys from camelCase to snake_case for MongoDB"""
        if 'job_id' not in data and 'jobId' in data:
            data['job_id'] = data.pop('jobId')
        if 'user_id' not in data and 'userId' in data:
            data['user_id'] = data.pop('userId')
        if 'cover_letter' not in data and 'coverLetter' in data:
            data['cover_letter'] = data.pop('coverLetter')
        return data


class ApplicationStatusUpdateSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf([
        ApplicationStatus.PENDING,
        ApplicationStatus.REVIEWING,
        ApplicationStatus.INTERVIEW,
        ApplicationStatus.REJECTED,
        ApplicationStatus.ACCEPTED
    ]))