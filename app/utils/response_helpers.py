from flask import g, jsonify

from app.utils.helpers import paginate_results
from app.utils.security import sanitize_user_data


def success_response(data, status_code=200, message=None):
    """Create standardized success response"""
    response = {"success": True, "data": data, "request_id": g.get("request_id")}

    if message:
        response["message"] = message

    return jsonify(response), status_code


def error_response(message, status_code=400, error_type="error"):
    """Create standardized error response"""
    return (
        jsonify(
            {
                "success": False,
                "error": error_type,
                "message": message,
                "request_id": g.get("request_id"),
            }
        ),
        status_code,
    )


def paginated_response(data, total_count, page, limit, status_code=200):
    """Create paginated response with metadata"""
    result = paginate_results(data, total_count, page, limit)
    return success_response(result, status_code)


def sanitize_response_data(data):
    """Remove sensitive fields from response data"""
    if isinstance(data, list):
        return [
            sanitize_user_data(item) if isinstance(item, dict) else item
            for item in data
        ]
    elif isinstance(data, dict):
        return sanitize_user_data(data)
    return data
