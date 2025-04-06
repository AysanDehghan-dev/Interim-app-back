from flask import current_app
from bson.objectid import ObjectId
import datetime


def get_db():
    """
    Get database connection
    """
    return current_app.db


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


def find_one(collection, query):
    """
    Find a document matching query
    """
    db = get_db()
    return db[collection].find_one(query)


def find_by_id(collection, id):
    """
    Find a document by its ID
    """
    db = get_db()
    return db[collection].find_one({"_id": ObjectId(id)})


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


def update_one(collection, id, updates):
    """
    Update a document by ID
    """
    db = get_db()
    # Always update the updated_at timestamp
    updates["updated_at"] = datetime.datetime.utcnow()
    result = db[collection].update_one({"_id": ObjectId(id)}, {"$set": updates})
    return result.modified_count


def delete_one(collection, id):
    """
    Delete a document by ID
    """
    db = get_db()
    result = db[collection].delete_one({"_id": ObjectId(id)})
    return result.deleted_count


def count_documents(collection, query=None):
    """
    Count documents matching query
    """
    db = get_db()
    return db[collection].count_documents(query or {})
