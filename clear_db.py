"""
Simple script to clear the database
"""
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

def clear_database():
    """Clear all data from the database"""
    # Get MongoDB URI from environment
    mongodb_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/interimapp")
    
    try:
        # Connect to MongoDB
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command("ping")
        
        # Get database name
        parsed_uri = urlparse(mongodb_uri)
        db_name = parsed_uri.path.lstrip('/') or 'interimapp'
        db = client[db_name]
        
        print(f"🗑️  Clearing database: {db_name}")
        
        # Collections to clear
        collections = ['users', 'companies', 'jobs', 'applications']
        
        total_deleted = 0
        for collection in collections:
            count = db[collection].count_documents({})
            if count > 0:
                result = db[collection].delete_many({})
                print(f"   • Deleted {result.deleted_count} documents from {collection}")
                total_deleted += result.deleted_count
            else:
                print(f"   • Collection {collection} was already empty")
        
        print(f"\n✅ Database cleared successfully!")
        print(f"📊 Total documents deleted: {total_deleted}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Failed to clear database: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    print("⚠️  This will permanently delete all data from the database!")
    confirm = input("Are you sure you want to continue? (yes/no): ")
    
    if confirm.lower() in ['yes', 'y']:
        clear_database()
    else:
        print("❌ Operation cancelled")