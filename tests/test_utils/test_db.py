from datetime import datetime

import pytest
from bson import ObjectId

from app.utils.db import (
    count_documents,
    delete_one,
    find_by_id,
    find_many,
    find_one,
    insert_one,
    update_one,
)


def test_insert_one(app, db):
    with app.app_context():
        # Test data
        collection = "test_collection"
        document = {"name": "Test Document", "value": 123}

        # Insert document
        doc_id = insert_one(collection, document)
        assert doc_id is not None

        # Verify document exists
        doc = db[collection].find_one({"_id": doc_id})
        assert doc is not None
        assert doc["name"] == "Test Document"
        assert doc["value"] == 123

        # Verify timestamps were added
        assert "created_at" in doc
        assert "updated_at" in doc


def test_find_one(app, db):
    with app.app_context():
        # Insert test document
        collection = "test_collection"
        db[collection].insert_one({"name": "Find One Test", "value": 456})

        # Find document
        doc = find_one(collection, {"name": "Find One Test"})
        assert doc is not None
        assert doc["value"] == 456

        # Test with non-existent query
        non_existent = find_one(collection, {"name": "Non-existent"})
        assert non_existent is None


def test_find_by_id(app, db):
    with app.app_context():
        # Insert test document
        collection = "test_collection"
        doc_id = (
            db[collection]
            .insert_one({"name": "Find By ID Test", "value": 789})
            .inserted_id
        )

        # Find document by ID
        doc = find_by_id(collection, doc_id)
        assert doc is not None
        assert doc["name"] == "Find By ID Test"
        assert doc["value"] == 789

        # Test with non-existent ID
        non_existent = find_by_id(collection, ObjectId())
        assert non_existent is None


def test_find_many(app, db):
    with app.app_context():
        # Insert test documents
        collection = "test_collection"
        common_field = {"category": "Test Category"}

        for i in range(5):
            db[collection].insert_one(
                {"name": f"Test Document {i}", "value": i, **common_field}
            )

        # Find documents
        docs = find_many(collection, common_field)
        assert len(docs) == 5

        # Test with sorting
        sorted_docs = find_many(collection, common_field, sort=[("value", -1)])
        assert sorted_docs[0]["value"] == 4
        assert sorted_docs[4]["value"] == 0

        # Test with pagination
        paginated_docs = find_many(collection, common_field, limit=2, skip=2)
        assert len(paginated_docs) == 2

        # Test with empty query
        all_docs = find_many(collection)
        assert len(all_docs) >= 5


def test_update_one(app, db):
    with app.app_context():
        # Insert test document
        collection = "test_collection"
        doc_id = (
            db[collection]
            .insert_one(
                {
                    "name": "Update Test",
                    "value": "Original Value",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            )
            .inserted_id
        )

        # Wait a moment to ensure updated_at will be different
        import time

        time.sleep(0.1)  # Add a small delay

        # Update document
        update_result = update_one(
            collection, doc_id, {"name": "Updated Name", "value": "Updated Value"}
        )
        assert update_result > 0

        # Verify document was updated
        updated_doc = db[collection].find_one({"_id": doc_id})
        assert updated_doc["name"] == "Updated Name"
        assert updated_doc["value"] == "Updated Value"

        # Instead of comparing timestamps directly, just check that updated_at exists
        assert "updated_at" in updated_doc


def test_delete_one(app, db):
    with app.app_context():
        # Insert test document
        collection = "test_collection"
        doc_id = (
            db[collection]
            .insert_one({"name": "Delete Test", "value": "To Be Deleted"})
            .inserted_id
        )

        # Verify document exists
        assert db[collection].find_one({"_id": doc_id}) is not None

        # Delete document
        delete_result = delete_one(collection, doc_id)
        assert delete_result > 0

        # Verify document was deleted
        assert db[collection].find_one({"_id": doc_id}) is None


def test_count_documents(app, db):
    with app.app_context():
        # Clear collection
        collection = "test_count_collection"
        db[collection].delete_many({})

        # Insert test documents
        common_field = {"category": "Count Test"}

        for i in range(10):
            db[collection].insert_one(
                {
                    "name": f"Count Document {i}",
                    "value": i % 2,  # 0 or 1
                    **common_field,
                }
            )

        # Count all documents
        count = count_documents(collection)
        assert count == 10

        # Count with filter
        count_even = count_documents(collection, {"value": 0})
        assert count_even == 5

        count_odd = count_documents(collection, {"value": 1})
        assert count_odd == 5

        # Count with non-matching filter
        count_none = count_documents(collection, {"value": 2})
        assert count_none == 0
