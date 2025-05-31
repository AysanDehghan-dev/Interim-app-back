class DatabaseError(Exception):
    """Custom exception for database operations"""

    pass


class InvalidObjectIdError(Exception):
    """Custom exception for invalid ObjectId"""

    pass


class DocumentNotFoundError(Exception):
    """Custom exception for when document is not found"""

    pass
