import pytest
from bson import ObjectId

from app.models.company import Company

def test_create_company(app, db):
    with app.app_context():
        # Test company data
        company_data = {
            'name': 'Acme Corp',
            'industry': 'Technology',
            'description': 'A fictional company',
            'email': 'contact@acme.example.com',
            'password': 'secure_password123'
        }
        
        # Create company
        company_id = Company.create(company_data)
        assert company_id is not None
        
        # Verify company was created in database
        company = db.companies.find_one({'_id': company_id})
        assert company is not None
        assert company['name'] == 'Acme Corp'
        assert company['industry'] == 'Technology'
        assert company['email'] == 'contact@acme.example.com'
        assert company['password'] != 'secure_password123'  # Password should be hashed
        
        # Verify default fields were initialized
        assert isinstance(company['jobs'], list)

def test_find_by_email(app, test_company):
    with app.app_context():
        # Find company by email
        company = Company.find_by_email(test_company['email'])
        assert company is not None
        assert str(company['_id']) == str(test_company['_id'])
        
        # Test with non-existent email
        non_existent = Company.find_by_email('non.existent@example.com')
        assert non_existent is None

def test_find_by_id(app, test_company):
    with app.app_context():
        # Find company by ID
        company = Company.find_by_id(test_company['_id'])
        assert company is not None
        assert company['email'] == test_company['email']
        
        # Test with non-existent ID
        non_existent = Company.find_by_id(ObjectId())
        assert non_existent is None

def test_find_all(app, test_company, db):
    with app.app_context():
        # Insert another company
        db.companies.insert_one({
            'name': 'Another Company',
            'industry': 'Finance',
            'description': 'Another test company',
            'email': 'another@example.com',
            'password': 'hashed_password'
        })
        
        # Find all companies
        companies = Company.find_all()
        assert len(companies) >= 2
        
        # Test with pagination
        limited_companies = Company.find_all(limit=1)
        assert len(limited_companies) == 1

def test_update_company(app, test_company):
    with app.app_context():
        # Update data
        update_data = {
            'name': 'Updated Company',
            'industry': 'Updated Industry',
            'website': 'https://updated-company.example.com'
        }
        
        # Update company
        result = Company.update(test_company['_id'], update_data)
        assert result > 0
        
        # Verify company was updated
        updated_company = Company.find_by_id(test_company['_id'])
        assert updated_company['name'] == 'Updated Company'
        assert updated_company['industry'] == 'Updated Industry'
        assert updated_company['website'] == 'https://updated-company.example.com'
        
        # Password shouldn't be updatable through this method
        update_with_password = {
            'password': 'new_password'
        }
        Company.update(test_company['_id'], update_with_password)
        updated_company = Company.find_by_id(test_company['_id'])
        # The password field shouldn't be changed
        assert updated_company['password'] == test_company['password']

def test_update_password(app, test_company, db):
    with app.app_context():
        # Original password hash
        original_password = test_company['password']
        
        # Update password
        Company.update_password(test_company['_id'], 'new_secure_password')
        
        # Verify password was updated
        updated_company = db.companies.find_one({'_id': test_company['_id']})
        assert updated_company['password'] != original_password

def test_authenticate(app, test_company):
    with app.app_context():
        # Set up a company with known credentials
        email = 'auth.test.company@example.com'
        password = 'test_password'
        
        company_data = {
            'name': 'Auth Test Company',
            'industry': 'Technology',
            'description': 'Company for authentication testing',
            'email': email,
            'password': password
        }
        
        Company.create(company_data)
        
        # Test successful authentication
        auth_company = Company.authenticate(email, password)
        assert auth_company is not None
        assert auth_company['email'] == email
        
        # Test failed authentication with wrong password
        failed_auth = Company.authenticate(email, 'wrong_password')
        assert failed_auth is None
        
        # Test failed authentication with non-existent email
        failed_auth = Company.authenticate('non.existent@example.com', password)
        assert failed_auth is None

def test_add_job(app, test_company, db):
    with app.app_context():
        # Create a job ID
        job_id = ObjectId()
        
        # Add job to company
        result = Company.add_job(test_company['_id'], job_id)
        assert result is True
        
        # Verify job was added
        updated_company = Company.find_by_id(test_company['_id'])
        assert str(job_id) in [str(j) for j in updated_company['jobs']]
        
        # Test adding the same job again (should return False)
        result = Company.add_job(test_company['_id'], job_id)
        assert result is False
        
        # Test with non-existent company
        result = Company.add_job(ObjectId(), job_id)
        assert result is False