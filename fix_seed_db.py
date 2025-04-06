#!/usr/bin/env python
import os
import datetime
from bson import ObjectId
from pymongo import MongoClient
from passlib.hash import pbkdf2_sha256

# Make sure the script can find the modules
import sys
sys.path.append('.')

# Connect to MongoDB
def connect_to_mongo():
    """Connect to MongoDB database"""
    import socket
    def is_mongo_available(host='mongo', port=27017, timeout=1):
        """Check if MongoDB is available at the given host and port"""
        try:
            socket.create_connection((host, port), timeout=timeout)
            return True
        except (socket.timeout, socket.error):
            return False

    # Try to connect to 'mongo' hostname (Docker), otherwise fallback to localhost
    if is_mongo_available(host='mongo'):
        MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://mongo:27017/interimapp')
    else:
        MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/interimapp')

    print(f"Connecting to MongoDB at {MONGODB_URI}")
    client = MongoClient(MONGODB_URI)
    db_name = MONGODB_URI.split('/')[-1]
    return client[db_name]

def main():
    """Update existing database to fix integration issues"""
    db = connect_to_mongo()
    
    # Check if we need to update job records to ensure they have company data
    jobs = list(db.jobs.find({}))
    
    for job in jobs:
        # Make sure each job has a proper companyId field
        if 'company_id' in job and isinstance(job['company_id'], ObjectId):
            # Find the company
            company = db.companies.find_one({"_id": job['company_id']})
            
            if company:
                # Update the job to include some company data directly
                db.jobs.update_one(
                    {"_id": job["_id"]},
                    {"$set": {
                        "company": {
                            "id": str(company["_id"]),
                            "name": company["name"],
                            "logo": company.get("logo", "https://placehold.co/64x64?text=Logo"),
                            "industry": company.get("industry", ""),
                            "description": company.get("description", "")
                        }
                    }}
                )
                print(f"Updated job {job['_id']} with company data")
    
    print("Database fix completed")

if __name__ == "__main__":
    main()