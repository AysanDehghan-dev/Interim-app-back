<<<<<<< HEAD
import datetime
import logging
from typing import Any, Dict, List, Optional
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
import datetime
=======
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)

<<<<<<< HEAD
from bson.objectid import InvalidId, ObjectId
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
from bson.objectid import ObjectId
=======
from bson.objectid import ObjectId
from bson.errors import InvalidId
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)
from flask import current_app
<<<<<<< HEAD
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom database exception"""

    pass


class InvalidObjectIdError(DatabaseError):
    """Raised when ObjectId is invalid"""

    pass
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
=======
from pymongo.errors import PyMongoError

from app.utils.exceptions import DatabaseError, InvalidObjectIdError, DocumentNotFoundError

logger = logging.getLogger(__name__)
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


def get_db():
<<<<<<< HEAD
    """Get database connection with error handling"""
    try:
        return current_app.db
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise DatabaseError("Database connection failed")
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
    """
    Get database connection
    """
    return current_app.db
=======
    """Get database connection"""
    try:
        return current_app.db
    except AttributeError:
        raise DatabaseError("Database connection not available")
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


<<<<<<< HEAD
def validate_object_id(id_str: str) -> ObjectId:
    """Validate and convert string to ObjectId"""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError) as e:
        logger.warning(f"Invalid ObjectId: {id_str}")
        raise InvalidObjectIdError(f"Invalid ID format: {id_str}")
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
def insert_one(collection, document):
    """
    Insert a document into collection and return inserted_id
    """
    db = get_db()
    # Add created_at and updated_at timestamps
    document["created_at"] = datetime.datetime.utcnow()
    document["updated_at"] = document["created_at"]
    result = db[collection].insert_one(document)
    return result.inserted_id
=======
def _validate_object_id(id_value: Union[str, ObjectId]) -> ObjectId:
    """Validate and convert string to ObjectId"""
    if isinstance(id_value, ObjectId):
        return id_value
    
    if not id_value:
        raise InvalidObjectIdError("ID cannot be empty")
    
    try:
        return ObjectId(id_value)
    except (InvalidId, TypeError) as e:
        raise InvalidObjectIdError(f"Invalid ObjectId format: {id_value}") from e
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


<<<<<<< HEAD
def insert_one(collection: str, document: Dict[str, Any]) -> ObjectId:
    """Insert a document with proper error handling"""
    try:
        db = get_db()
        # Add timestamps
        now = datetime.datetime.utcnow()
        document.update({"created_at": now, "updated_at": now})

        result = db[collection].insert_one(document)
        logger.info(f"Document inserted in {collection}: {result.inserted_id}")
        return result.inserted_id

    except PyMongoError as e:
        logger.error(f"Database error inserting into {collection}: {str(e)}")
        raise DatabaseError(f"Failed to insert document: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error inserting into {collection}: {str(e)}")
        raise DatabaseError("Unexpected database error")
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
def find_one(collection, query):
    """
    Find a document matching query
    """
    db = get_db()
    return db[collection].find_one(query)
=======
def _add_timestamps(document: Dict, is_update: bool = False) -> Dict:
    """Add timestamps to document"""
    now = datetime.utcnow()
    
    if not is_update and "created_at" not in document:
        document["created_at"] = now
    
    document["updated_at"] = now
    return document
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


<<<<<<< HEAD
def find_one(collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find a document matching query"""
    try:
        db = get_db()
        return db[collection].find_one(query)
    except PyMongoError as e:
        logger.error(f"Database error finding one in {collection}: {str(e)}")
        raise DatabaseError(f"Failed to find document: {str(e)}")
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
def find_by_id(collection, id):
    """
    Find a document by its ID
    """
    db = get_db()
    return db[collection].find_one({"_id": ObjectId(id)})
=======
def insert_one(collection: str, document: Dict) -> ObjectId:
    """Insert a document into collection and return inserted_id"""
    try:
        db = get_db()
        
        # Add timestamps
        document = _add_timestamps(document.copy())
        
        result = db[collection].insert_one(document)
        
        logger.debug(f"Inserted document in {collection}: {result.inserted_id}")
        return result.inserted_id
        
    except PyMongoError as e:
        logger.error(f"Database error inserting into {collection}: {str(e)}")
        raise DatabaseError(f"Failed to insert document: {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error inserting into {collection}: {str(e)}")
        raise DatabaseError(f"Unexpected error during insert: {str(e)}") from e
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


<<<<<<< HEAD
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
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
def find_many(collection, query=None, sort=None, limit=0, skip=0):
    """
    Find documents matching query with optional sorting and pagination
    """
    db = get_db()
    cursor = db[collection].find(query or {})

    if sort:
        cursor = cursor.sort(sort)

    if skip:
        cursor = cursor.skip(skip)

    if limit:
        cursor = cursor.limit(limit)

    return list(cursor)
=======
def insert_many(collection: str, documents: List[Dict]) -> List[ObjectId]:
    """Insert multiple documents into collection"""
    try:
        db = get_db()
        
        # Add timestamps to all documents
        timestamped_docs = []
        for doc in documents:
            timestamped_docs.append(_add_timestamps(doc.copy()))
        
        result = db[collection].insert_many(timestamped_docs)
        
        logger.debug(f"Inserted {len(result.inserted_ids)} documents in {collection}")
        return result.inserted_ids
        
    except PyMongoError as e:
        logger.error(f"Database error inserting many into {collection}: {str(e)}")
        raise DatabaseError(f"Failed to insert documents: {str(e)}") from e
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


<<<<<<< HEAD
def find_many(
    collection: str,
    query: Optional[Dict[str, Any]] = None,
    sort: Optional[List[tuple]] = None,
    limit: int = 0,
    skip: int = 0,
    max_limit: int = 100,
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
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
def update_one(collection, id, updates):
    """
    Update a document by ID
    """
    db = get_db()
    # Always update the updated_at timestamp
    updates["updated_at"] = datetime.datetime.utcnow()
    result = db[collection].update_one({"_id": ObjectId(id)}, {"$set": updates})
    return result.modified_count
=======
def find_one(collection: str, query: Dict, projection: Optional[Dict] = None) -> Optional[Dict]:
    """Find a document matching query"""
    try:
        db = get_db()
        
        result = db[collection].find_one(query, projection)
        
        if result:
            logger.debug(f"Found document in {collection} with query: {query}")
        else:
            logger.debug(f"No document found in {collection} with query: {query}")
            
        return result
        
    except PyMongoError as e:
        logger.error(f"Database error finding in {collection}: {str(e)}")
        raise DatabaseError(f"Failed to find document: {str(e)}") from e
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


<<<<<<< HEAD
def update_one(collection: str, id_str: str, updates: Dict[str, Any]) -> int:
    """Update document with validation"""
    try:
        db = get_db()
        object_id = validate_object_id(id_str)

        # Always update timestamp
        updates["updated_at"] = datetime.datetime.utcnow()

        result = db[collection].update_one({"_id": object_id}, {"$set": updates})

        logger.info(f"Document updated in {collection}: {id_str}")
        return result.modified_count

    except InvalidObjectIdError:
        return 0  # Invalid ID returns 0 modified
    except PyMongoError as e:
        logger.error(f"Database error updating {collection}: {str(e)}")
        raise DatabaseError(f"Failed to update document: {str(e)}")
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
def delete_one(collection, id):
    """
    Delete a document by ID
    """
    db = get_db()
    result = db[collection].delete_one({"_id": ObjectId(id)})
    return result.deleted_count
=======
def find_by_id(collection: str, id_value: Union[str, ObjectId], projection: Optional[Dict] = None) -> Optional[Dict]:
    """Find a document by its ID"""
    try:
        object_id = _validate_object_id(id_value)
        return find_one(collection, {"_id": object_id}, projection)
        
    except InvalidObjectIdError:
        # Re-raise ObjectId validation errors
        raise
    except Exception as e:
        logger.error(f"Error finding by ID in {collection}: {str(e)}")
        raise DatabaseError(f"Failed to find document by ID: {str(e)}") from e
>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)


<<<<<<< HEAD
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
||||||| parent of 2c0145b (feat: Add database management scripts and improve configuration)
def count_documents(collection, query=None):
    """
    Count documents matching query
    """
    db = get_db()
    return db[collection].count_documents(query or {})
=======
def find_many(
    collection: str, 
    query: Optional[Dict] = None, 
    sort: Optional[List] = None, 
    limit: int = 0, 
    skip: int = 0,
    projection: Optional[Dict] = None
) -> List[Dict]:
    """Find documents matching query with optional sorting and pagination"""
    try:
        db = get_db()
        
        cursor = db[collection].find(query or {}, projection)
        
        if sort:
            cursor = cursor.sort(sort)
        
        if skip > 0:
            cursor = cursor.skip(skip)
        
        if limit > 0:
            cursor = cursor.limit(limit)
        
        results = list(cursor)
        
        logger.debug(f"Found {len(results)} documents in {collection}")
        return results
        
    except PyMongoError as e:
        logger.error(f"Database error finding many in {collection}: {str(e)}")
        raise DatabaseError(f"Failed to find documents: {str(e)}") from e


def update_one(collection: str, id_value: Union[str, ObjectId], updates: Dict) -> int:
    """Update a document by ID and return modified count"""
    try:
        object_id = _validate_object_id(id_value)
        db = get_db()
        
        # Add update timestamp
        updates = _add_timestamps(updates.copy(), is_update=True)
        
        result = db[collection].update_one(
            {"_id": object_id}, 
            {"$set": updates}
        )
        
        logger.debug(f"Updated document in {collection}: {object_id}, modified: {result.modified_count}")
        return result.modified_count
        
    except InvalidObjectIdError:
        # Re-raise ObjectId validation errors
        raise
    except PyMongoError as e:
        logger.error(f"Database error updating in {collection}: {str(e)}")
        raise DatabaseError(f"Failed to update document: {str(e)}") from e


def update_many(collection: str, query: Dict, updates: Dict) -> int:
    """Update multiple documents matching query"""
    try:
        db = get_db()
        
        # Add update timestamp
        updates = _add_timestamps(updates.copy(), is_update=True)
        
        result = db[collection].update_many(query, {"$set": updates})
        
        logger.debug(f"Updated {result.modified_count} documents in {collection}")
        return result.modified_count
        
    except PyMongoError as e:
        logger.error(f"Database error updating many in {collection}: {str(e)}")
        raise DatabaseError(f"Failed to update documents: {str(e)}") from e


def delete_one(collection: str, id_value: Union[str, ObjectId]) -> int:
    """Delete a document by ID and return deleted count"""
    try:
        object_id = _validate_object_id(id_value)
        db = get_db()
        
        result = db[collection].delete_one({"_id": object_id})
        
        logger.debug(f"Deleted document in {collection}: {object_id}, deleted: {result.deleted_count}")
        return result.deleted_count
        
    except InvalidObjectIdError:
        # Re-raise ObjectId validation errors
        raise
    except PyMongoError as e:
        logger.error(f"Database error deleting in {collection}: {str(e)}")
        raise DatabaseError(f"Failed to delete document: {str(e)}") from e


def delete_many(collection: str, query: Dict) -> int:
    """Delete multiple documents matching query"""
    try:
        db = get_db()
        
        result = db[collection].delete_many(query)
        
        logger.debug(f"Deleted {result.deleted_count} documents in {collection}")
        return result.deleted_count
        
    except PyMongoError as e:
        logger.error(f"Database error deleting many in {collection}: {str(e)}")
        raise DatabaseError(f"Failed to delete documents: {str(e)}") from e


def count_documents(collection: str, query: Optional[Dict] = None) -> int:
    """Count documents matching query"""
    try:
        db = get_db()
        
        count = db[collection].count_documents(query or {})
        
        logger.debug(f"Counted {count} documents in {collection}")
        return count
        
    except PyMongoError as e:
        logger.error(f"Database error counting in {collection}: {str(e)}")
        raise DatabaseError(f"Failed to count documents: {str(e)}") from e


def aggregate(collection: str, pipeline: List[Dict]) -> List[Dict]:
    """Run aggregation pipeline on collection"""
    try:
        db = get_db()
        
        results = list(db[collection].aggregate(pipeline))
        
        logger.debug(f"Aggregation on {collection} returned {len(results)} results")
        return results
        
    except PyMongoError as e:
        logger.error(f"Database error in aggregation for {collection}: {str(e)}")
        raise DatabaseError(f"Failed to run aggregation: {str(e)}") from e


def ensure_document_exists(collection: str, id_value: Union[str, ObjectId]) -> Dict:
    """Find document by ID or raise DocumentNotFoundError"""
    document = find_by_id(collection, id_value)
    
    if not document:
        raise DocumentNotFoundError(f"Document not found in {collection} with ID: {id_value}")
    
    return document


def create_index(collection: str, keys: Union[str, List], **kwargs):
    """Create an index on collection"""
    try:
        db = get_db()
        
        result = db[collection].create_index(keys, **kwargs)
        
        logger.info(f"Created index on {collection}: {result}")
        return result
        
    except PyMongoError as e:
        logger.error(f"Database error creating index on {collection}: {str(e)}")
        raise DatabaseError(f"Failed to create index: {str(e)}") from e

>>>>>>> 2c0145b (feat: Add database management scripts and improve configuration)
