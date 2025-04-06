from marshmallow import (
    Schema,
    fields,
    validate,
    post_load,
    pre_dump,
    validates_schema,
    ValidationError,
)
from bson import ObjectId


class CompanySchema(Schema):
    id = fields.Str()
    name = fields.Str(required=True, validate=validate.Length(min=1))
    industry = fields.Str(required=True)
    description = fields.Str(required=True)
    logo = fields.Str()
    website = fields.Str()
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, validate=validate.Length(min=6))
    phone = fields.Str()
    address = fields.Str()
    city = fields.Str()
    country = fields.Str()
    jobs = fields.List(fields.Str(), dump_only=True)
    createdAt = fields.DateTime(attribute="created_at", dump_only=True)
    updatedAt = fields.DateTime(attribute="updated_at", dump_only=True)

    # Convert keys from snake_case to camelCase
    class Meta:
        ordered = True

    @pre_dump
    def prepare_data(self, data, **kwargs):
        """Convert ObjectId to string and prepare data for serialization"""
        if data and "_id" in data:
            data["id"] = str(data["_id"])

        # Convert job ObjectId list to string list
        if data and "jobs" in data:
            data["jobs"] = [str(job_id) for job_id in data["jobs"]]

        return data


class CompanyLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

    class Meta:
        ordered = True


class CompanyRegisterSchema(CompanySchema):
    password = fields.Str(required=True, validate=validate.Length(min=6))
    confirmPassword = fields.Str(required=True)

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        """Validate that password and confirmPassword match"""
        if data.get("password") != data.get("confirmPassword"):
            raise ValidationError("Passwords must match", "confirmPassword")

    class Meta:
        ordered = True
