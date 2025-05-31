import re

from bson import ObjectId
from marshmallow import Schema
from marshmallow import ValidationError as MarshmallowValidationError
from marshmallow import fields, post_load, pre_dump


class ObjectIdField(fields.Field):
    """Custom field for MongoDB ObjectId"""

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs):
        if not value:
            return None
        try:
            return ObjectId(value)
        except Exception:
            raise MarshmallowValidationError(f"Invalid ObjectId: {value}")


class EnumField(fields.Field):
    """Custom field for enum validation"""

    def __init__(self, enum_class, *args, **kwargs):
        self.enum_class = enum_class
        super().__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        if not value:
            return None
        if not self.enum_class.is_valid(value):
            valid_values = ", ".join(self.enum_class.get_all())
            raise MarshmallowValidationError(
                f"Invalid value. Must be one of: {valid_values}"
            )
        return value


class PhoneField(fields.Field):
    """Custom field for phone number validation"""

    def _serialize(self, value, attr, obj, **kwargs):
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        if not value:
            return None

        # Remove all non-digit characters for validation
        digits_only = re.sub(r"\D", "", value)

        # Check if it has at least 10 digits
        if len(digits_only) < 10:
            raise MarshmallowValidationError(
                "Phone number must have at least 10 digits"
            )

        return value


class URLField(fields.Url):
    """Enhanced URL field with better validation"""

    def _deserialize(self, value, attr, data, **kwargs):
        if not value:
            return None

        # Add http:// if no protocol specified
        if not value.startswith(("http://", "https://")):
            value = "https://" + value

        return super()._deserialize(value, attr, data, **kwargs)


class BaseSchema(Schema):
    """Base schema with common functionality"""

    class Meta:
        ordered = True

    @pre_dump
    def prepare_data(self, data, **kwargs):
        """Convert ObjectId to string and prepare data for serialization"""
        if not data:
            return data

        # Convert _id to id
        if "_id" in data:
            data["id"] = str(data["_id"])

        return data

    @post_load
    def clean_data(self, data, **kwargs):
        """Clean and validate data after loading"""
        # Remove None values to avoid overwriting existing data
        return {k: v for k, v in data.items() if v is not None}


class TimestampMixin:
    """Mixin for schemas with timestamps"""

    created_at = fields.DateTime(data_key="createdAt", dump_only=True)
    updated_at = fields.DateTime(data_key="updatedAt", dump_only=True)


class PaginationSchema(BaseSchema):
    """Reusable pagination schema"""

    page = fields.Int(missing=1, validate=lambda x: x > 0)
    limit = fields.Int(missing=20, validate=lambda x: 1 <= x <= 100)

    @post_load
    def calculate_skip(self, data, **kwargs):
        """Calculate skip value for database queries"""
        data["skip"] = (data["page"] - 1) * data["limit"]
        return data
