import pytest
from bson import ObjectId
from datetime import datetime

from app.models.job import Job, JobType

def test_create_job(app, test_company, db):
    with app.app_context():
        # Test job data
        job_data = {
            'title': 'Software Engineer',
            'company_id': test_company['_id'],
            'description': 'A job for software engineers',
            'requirements': ['Python', 'Flask', 'MongoDB'],
            'location': 'Remote',
            'type': JobType.FULL_TIME,
            'salary': {
                'min': 60000,
                'max': 80000,
                'currency': 'USD'
            }
        }
        
        # Create job
        job_id = Job.create(job_data)
        assert job_id is not None
        
        # Verify job was created in database
        job = db.jobs.find_one({'_id': job_id})
        assert job is not None
        assert job['title'] == 'Software Engineer'
        assert job['description'] == 'A job for software engineers'
        assert len(job['requirements']) == 3
        assert job['type'] == JobType.FULL_TIME
        
        # Verify default fields were initialized
        assert isinstance(job['applications'], list)
        assert 'created_at' in job
        assert 'updated_at' in job
        assert 'start_date' in job

def test_find_by_id(app, test_job):
    with app.app_context():
        # Find job by ID
        job = Job.find_by_id(test_job['_id'])
        assert job is not None
        assert job['title'] == test_job['title']
        
        # Test with non-existent ID
        non_existent = Job.find_by_id(ObjectId())
        assert non_existent is None

def test_find_by_company(app, test_company, test_job, db):
    with app.app_context():
        # Add another job for the same company
        another_job_data = {
            'title': 'Product Manager',
            'company_id': test_company['_id'],
            'description': 'A job for product managers',
            'requirements': ['Product Management', 'Agile'],
            'location': 'Office',
            'type': JobType.FULL_TIME,
            'applications': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'start_date': datetime.utcnow()
        }
        another_job_id = db.jobs.insert_one(another_job_data).inserted_id
        
        # Find jobs by company
        jobs = Job.find_by_company(test_company['_id'])
        assert len(jobs) >= 2
        job_ids = [str(job['_id']) for job in jobs]
        assert str(test_job['_id']) in job_ids
        assert str(another_job_id) in job_ids
        
        # Test with pagination
        limited_jobs = Job.find_by_company(test_company['_id'], limit=1)
        assert len(limited_jobs) == 1

def test_search_jobs(app, test_job, db):
    with app.app_context():
        # Add more jobs with different attributes for testing search
        jobs_to_add = [
            {
                'title': 'Frontend Developer',
                'company_id': test_job['company_id'],
                'description': 'A job for frontend developers with React',
                'requirements': ['JavaScript', 'React', 'CSS'],
                'location': 'New York',
                'type': JobType.CONTRACT,
                'applications': [],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'start_date': datetime.utcnow()
            },
            {
                'title': 'Data Scientist',
                'company_id': test_job['company_id'],
                'description': 'A job for data scientists',
                'requirements': ['Python', 'Machine Learning', 'SQL'],
                'location': 'Remote',
                'type': JobType.PART_TIME,
                'applications': [],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'start_date': datetime.utcnow()
            }
        ]
        
        for job in jobs_to_add:
            db.jobs.insert_one(job)
        
        # Test search with keyword
        results = Job.search({'keyword': 'python'})
        assert len(results) >= 2  # Test job and Data Scientist both have Python
        
        # Test search with location
        results = Job.search({'location': 'new york'})
        assert len(results) >= 1
        assert any(job['location'] == 'New York' for job in results)
        
        # Test search with job type
        results = Job.search({'type': JobType.CONTRACT})
        assert len(results) >= 1
        assert all(job['type'] == JobType.CONTRACT for job in results)
        
        # Test search with company_id
        results = Job.search({'company_id': str(test_job['company_id'])})
        assert len(results) >= 3  # Test job + 2 added jobs
        
        # Test search with multiple filters
        results = Job.search({
            'keyword': 'developer',
            'type': JobType.CONTRACT
        })
        assert len(results) >= 1
        assert all(job['type'] == JobType.CONTRACT for job in results)
        
        # Test search with pagination
        results = Job.search({}, limit=2)
        assert len(results) == 2

def test_count_jobs(app, test_job, db):
    with app.app_context():
        # Count all jobs
        count = Job.count()
        assert count >= 1
        
        # Count with filters
        count = Job.count({'type': test_job['type']})
        assert count >= 1
        
        # Count with location filter
        count = Job.count({'location': test_job['location']})
        assert count >= 1
        
        # Test count with non-matching filter
        count = Job.count({'location': 'Non-existent Location'})
        assert count == 0

def test_update_job(app, test_job):
    with app.app_context():
        # Update data
        update_data = {
            'title': 'Updated Job Title',
            'description': 'Updated job description',
            'salary': {
                'min': 65000,
                'max': 85000,
                'currency': 'USD'
            }
        }
        
        # Update job
        result = Job.update(test_job['_id'], update_data)
        assert result > 0
        
        # Verify job was updated
        updated_job = Job.find_by_id(test_job['_id'])
        ass