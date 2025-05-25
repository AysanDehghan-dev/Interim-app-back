import datetime
import logging
from typing import Dict, List, Optional, Any

from bson.objectid import ObjectId, InvalidId
from flask import current_app
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom database exception"""
    pass

class InvalidObjectIdError(DatabaseError):
    """Raised when ObjectId is invalid"""
    pass

def get_db():
    """Get database connection with error handling"""
    try:
        return current_app.db
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise DatabaseError("Database connection failed")

def validate_object_id(id_str: str) -> ObjectId:
    """Validate and convert string to ObjectId"""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError) as e:
        logger.warning(f"Invalid ObjectId: {id_str}")
        raise InvalidObjectIdError(f"Invalid ID format: {id_str}")

def insert_one(collection: str, document: Dict[str, Any]) -> ObjectId:
    """Insert a document with proper error handling"""
    try:
        db = get_db()
        # Add timestamps
        now = datetime.datetime.utcnow()
        document.update({
            "created_at": now,
            "updated_at": now
        })
        
        result = db[collection].insert_one(document)
        logger.info(f"Document inserted in {collection}: {result.inserted_id}")
        return result.inserted_id
        
    except PyMongoError as e:
        logger.error(f"Database error inserting into {collection}: {str(e)}")
        raise DatabaseError(f"Failed to insert document: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error inserting into {collection}: {str(e)}")
        raise DatabaseError("Unexpected database error")

def find_one(collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find a document matching query"""
    try:
        db = get_db()
        return db[collection].find_one(query)
    except PyMongoError as e:
        logger.error(f"Database error finding one in {collection}: {str(e)}")
        raise DatabaseError(f"Failed to find document: {str(e)}")

def find_by_id(collection: str, id_str: str) -> Optional[Dict[str, Any]]:
    """Find document by ID with validation"""
    try:
        db = get_db()
        object_id = validate_object_id(id_str)
        return db[collection].find_one({"_id": object_id})
        
    except InvalidObjectIdError:
        return None  # Invalid ID returns None instead of crashing
    except PyMongoError as e:
        logger.error(f"Database error finding in {collection}: {str(e)}")
        raise DatabaseError(f"Failed to find document: {str(e)}")

def find_many(
    collection: str, 
    query: Optional[Dict[str, Any]] = None, 
    sort: Optional[List[tuple]] = None, 
    limit: int = 0, 
    skip: int = 0,
    max_limit: int = 100
) -> List[Dict[str, Any]]:
    """Find documents with safety limits"""
    try:
        db = get_db()
        
        # Enforce maximum limit for performance
        if limit > max_limit:
            limit = max_limit
            logger.warning(f"Limit capped at {max_limit}")
        
        cursor = db[collection].find(query or {})
        
        if sort:
            cursor = cursor.sort(sort)
        if skip > 0:
            cursor = cursor.skip(skip)
        if limit > 0:
            cursor = cursor.limit(limit)
            
        return list(cursor)
        
    except PyMongoError as e:
        logger.error(f"Database error querying {collection}: {str(e)}")
        raise DatabaseError(f"Failed to query documents: {str(e)}")

def update_one(collection: str, id_str: str, updates: Dict[str, Any]) -> int:
    """Update document with validation"""
    try:
        db = get_db()
        object_id = validate_object_id(id_str)
        
        # Always update timestamp
        updates["updated_at"] = datetime.datetime.utcnow()
        
        result = db[collection].update_one(
            {"_id": object_id}, 
            {"$set": updates}
        )
        
        logger.info(f"Document updated in {collection}: {id_str}")
        return result.modified_count
        
    except InvalidObjectIdError:
        return 0  # Invalid ID returns 0 modified
    except PyMongoError as e:
        logger.error(f"Database error updating {collection}: {str(e)}")
        raise DatabaseError(f"Failed to update document: {str(e)}")

def delete_one(collection: str, id_str: str) -> int:
    """Delete a document by ID"""
    try:
        db = get_db()
        object_id = validate_object_id(id_str)
        
        result = db[collection].delete_one({"_id": object_id})
        logger.info(f"Document deleted from {collection}: {id_str}")
        return result.deleted_count
        
    except InvalidObjectIdError:
        return 0  # Invalid ID returns 0 deleted
    except PyMongoError as e:
        logger.error(f"Database error deleting from {collection}: {str(e)}")
        raise DatabaseError(f"Failed to delete document: {str(e)}")

def count_documents(collection: str, query: Optional[Dict[str, Any]] = None) -> int:
    """Count documents matching query"""
    try:
        db = get_db()
        return db[collection].count_documents(query or {})
    except PyMongoError as e:
        logger.error(f"Database error counting in {collection}: {str(e)}")
        raise DatabaseError(f"Failed to count documents: {str(e)}")