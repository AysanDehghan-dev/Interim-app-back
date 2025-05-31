import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import current_app
from pymongo.errors import PyMongoError

from app.utils.exceptions import (
    DatabaseError,
    DocumentNotFoundError,
    InvalidObjectIdError,
)

logger = logging.getLogger(__name__)


def get_db():
    """Get database connection"""
    try:
        return current_app.db
    except AttributeError:
        raise DatabaseError("Database connection not available")


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


def _add_timestamps(document: Dict, is_update: bool = False) -> Dict:
    """Add timestamps to document"""
    now = datetime.utcnow()

    if not is_update and "created_at" not in document:
        document["created_at"] = now

    document["updated_at"] = now
    return document


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


def find_one(
    collection: str, query: Dict, projection: Optional[Dict] = None
) -> Optional[Dict]:
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


def find_by_id(
    collection: str, id_value: Union[str, ObjectId], projection: Optional[Dict] = None
) -> Optional[Dict]:
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


def find_many(
    collection: str,
    query: Optional[Dict] = None,
    sort: Optional[List] = None,
    limit: int = 0,
    skip: int = 0,
    projection: Optional[Dict] = None,
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

        result = db[collection].update_one({"_id": object_id}, {"$set": updates})

        logger.debug(
            f"Updated document in {collection}: {object_id}, modified: {result.modified_count}"
        )
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

        logger.debug(
            f"Deleted document in {collection}: {object_id}, deleted: {result.deleted_count}"
        )
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
        raise DocumentNotFoundError(
            f"Document not found in {collection} with ID: {id_value}"
        )

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
