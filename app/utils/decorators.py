import functools
import logging
from flask import jsonify, request, g
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from marshmallow import ValidationError as MarshmallowValidationError

from app.utils.exceptions import DatabaseError, InvalidObjectIdError, DocumentNotFoundError
from app.models.exceptions import ValidationError

logger = logging.getLogger(__name__)


def handle_errors(f):
    """Decorator to handle common errors across all routes"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except MarshmallowValidationError as e:
            logger.warning(f"[{g.get('request_id')}] Validation error: {e.messages}")
            return jsonify({
                "error": "Validation error",
                "messages": e.messages,
                "request_id": g.get('request_id')
            }), 400
        except ValidationError as e:
            logger.warning(f"[{g.get('request_id')}] Model validation error: {str(e)}")
            return jsonify({
                "error": "Validation error",
                "message": str(e),
                "request_id": g.get('request_id')
            }), 400
        except InvalidObjectIdError as e:
            logger.warning(f"[{g.get('request_id')}] Invalid ObjectId: {str(e)}")
            return jsonify({
                "error": "Invalid ID",
                "message": str(e),
                "request_id": g.get('request_id')
            }), 400
        except DocumentNotFoundError as e:
            logger.info(f"[{g.get('request_id')}] Document not found: {str(e)}")
            return jsonify({
                "error": "Not found",
                "message": str(e),
                "request_id": g.get('request_id')
            }), 404
        except DatabaseError as e:
            logger.error(f"[{g.get('request_id')}] Database error: {str(e)}")
            return jsonify({
                "error": "Database error",
                "message": "Please try again later",
                "request_id": g.get('request_id')
            }), 500
        except Exception as e:
            logger.error(f"[{g.get('request_id')}] Unexpected error: {str(e)}")
            return jsonify({
                "error": "Internal server error",
                "message": "Something went wrong",
                "request_id": g.get('request_id')
            }), 500
    
    return decorated_function


def validate_json(schema_class):
    """Decorator to validate request JSON using schema"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    "error": "Content-Type must be application/json",
                    "request_id": g.get('request_id')
                }), 400
            
            if not request.json:
                return jsonify({
                    "error": "Request body cannot be empty",
                    "request_id": g.get('request_id')
                }), 400
            
            schema = schema_class()
            validated_data = schema.load(request.json)
            
            # Add validated data to kwargs
            kwargs['validated_data'] = validated_data
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_user_type(user_type):
    """Decorator to require specific user type (user/company)"""
    def decorator(f):
        @functools.wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            claims = get_jwt()
            current_user_type = claims.get("user_type", "")
            
            if current_user_type != user_type:
                return jsonify({
                    "error": "Access denied",
                    "message": f"This endpoint requires {user_type} access",
                    "request_id": g.get('request_id')
                }), 403
            
            # Add user info to kwargs
            kwargs['current_user_id'] = get_jwt_identity()
            kwargs['current_user_type'] = current_user_type
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_pagination(f):
    """Decorator to validate and process pagination parameters"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
            
            if page < 1:
                page = 1
            if limit < 1 or limit > 100:
                limit = 20
            
            skip = (page - 1) * limit
            
            kwargs['pagination'] = {
                'page': page,
                'limit': limit,
                'skip': skip
            }
            
            return f(*args, **kwargs)
        except ValueError:
            return jsonify({
                "error": "Invalid pagination parameters",
                "message": "Page and limit must be positive integers",
                "request_id": g.get('request_id')
            }), 400
    
    return decorated_function