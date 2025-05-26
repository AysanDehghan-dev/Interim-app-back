import json

import pytest
from bson import ObjectId


def test_get_companies(client):
    """Test getting list of companies with pagination"""
    # Get list of companies
    response = client.get("/api/companies")

    # Should always return 200, even if no companies exist
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check the response structure matches your paginated API
    assert isinstance(data, dict)
    assert "companies" in data
    assert "pagination" in data
    
    # Check companies is a list (could be empty)
    assert isinstance(data["companies"], list)
    
    # Check pagination structure
    pagination = data["pagination"]
    assert isinstance(pagination, dict)
    assert "page" in pagination
    assert "limit" in pagination
    assert "total" in pagination
    assert "pages" in pagination


def test_get_companies_with_pagination(client):
    """Test getting companies with specific pagination parameters"""
    # Get companies with pagination
    response = client.get("/api/companies?page=1&limit=2")

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check response structure
    assert isinstance(data, dict)
    assert "companies" in data
    assert "pagination" in data
    
    # Check pagination values
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["limit"] == 2
    
    # Companies list should not exceed limit
    assert len(data["companies"]) <= 2


def test_get_company_by_id(client, test_company):
    """Test getting a specific company by ID"""
    # Get company by ID
    response = client.get(f'/api/companies/{test_company["_id"]}')

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == test_company["name"]
    assert data["industry"] == test_company["industry"]
    assert data["email"] == test_company["email"]
    # Check that password is not exposed
    assert "password" not in data


def test_get_company_by_id_not_found(client):
    """Test getting non-existent company"""
    # Try to get non-existent company
    random_id = str(ObjectId())
    response = client.get(f"/api/companies/{random_id}")

    # Check response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data
    assert "not found" in data["error"].lower()


def test_get_company_by_invalid_id(client):
    """Test getting company with invalid ID format"""
    # Try to get company with invalid ID
    response = client.get("/api/companies/invalid-id")

    # Check response - should handle invalid ObjectId gracefully
    assert response.status_code in [400, 404]  # Depending on your error handling
    data = json.loads(response.data)
    assert "error" in data


def test_get_company_profile(client, company_auth_headers):
    """Test getting authenticated company's profile"""
    # Get company profile
    response = client.get("/api/companies/profile", headers=company_auth_headers)

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "name" in data
    assert "industry" in data
    assert "email" in data
    # Ensure password is not exposed
    assert "password" not in data


def test_get_company_profile_unauthorized(client):
    """Test getting company profile without authentication"""
    # Try to get company profile without authentication
    response = client.get("/api/companies/profile")

    # Check response
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data


def test_get_company_profile_with_user_token(client, auth_headers):
    """Test getting company profile with user token (should fail)"""
    # Try to get company profile with user token
    response = client.get("/api/companies/profile", headers=auth_headers)

    # Check response
    assert response.status_code == 403
    data = json.loads(response.data)
    assert "error" in data
    assert "Access denied" in data["error"]


def test_update_company_profile(client, company_auth_headers):
    """Test updating company profile"""
    # Update data
    update_data = {
        "name": "Updated Company",
        "industry": "Updated Industry",
        "website": "https://updated-company.example.com",
        "description": "Updated description",
    }

    # Update profile
    response = client.put(
        "/api/companies/profile",
        data=json.dumps(update_data),
        content_type="application/json",
        headers=company_auth_headers,
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == "Updated Company"
    assert data["industry"] == "Updated Industry"
    assert data["website"] == "https://updated-company.example.com"
    assert data["description"] == "Updated description"
    # Ensure password is not in response
    assert "password" not in data


def test_update_company_profile_with_email_password(client, company_auth_headers):
    """Test updating profile with email/password (should be ignored)"""
    # Try to update profile with email and password (should be ignored)
    update_data = {
        "name": "Another Company Update",
        "email": "new.email@example.com",
        "password": "new_password",
    }

    # Update profile
    response = client.put(
        "/api/companies/profile",
        data=json.dumps(update_data),
        content_type="application/json",
        headers=company_auth_headers,
    )

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == "Another Company Update"
    assert data["email"] != "new.email@example.com"  # Email should not be updated
    assert "password" not in data


def test_update_company_profile_unauthorized(client):
    """Test updating company profile without authentication"""
    update_data = {"name": "Unauthorized Update"}
    
    response = client.put(
        "/api/companies/profile",
        data=json.dumps(update_data),
        content_type="application/json",
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data


def test_update_company_profile_with_user_token(client, auth_headers):
    """Test updating company profile with user token (should fail)"""
    update_data = {"name": "User Trying to Update Company"}
    
    response = client.put(
        "/api/companies/profile",
        data=json.dumps(update_data),
        content_type="application/json",
        headers=auth_headers,
    )
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert "error" in data


def test_get_company_jobs(client, company_auth_headers, test_job):
    """Test getting jobs posted by authenticated company"""
    # Get company jobs
    response = client.get("/api/companies/jobs", headers=company_auth_headers)

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    
    # If there are jobs, check their structure
    if len(data) > 0:
        job = data[0]
        assert isinstance(job, dict)
        assert "id" in job
        assert "title" in job
        assert "companyId" in job


def test_get_company_jobs_unauthorized(client):
    """Test getting company jobs without authentication"""
    response = client.get("/api/companies/jobs")
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data


def test_get_company_jobs_with_user_token(client, auth_headers):
    """Test getting company jobs with user token (should fail)"""
    response = client.get("/api/companies/jobs", headers=auth_headers)
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert "error" in data


def test_get_jobs_by_company(client, test_company, test_job):
    """Test getting jobs by specific company ID (public endpoint)"""
    # Get jobs by company ID
    response = client.get(f'/api/companies/{test_company["_id"]}/jobs')

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)

    # If there are jobs, verify job data structure
    if len(data) > 0:
        # Try to find our test job
        job = next((j for j in data if str(j["id"]) == str(test_job["_id"])), None)
        if job is not None:
            assert job["title"] == test_job["title"]
            assert job["location"] == test_job["location"]
            assert job["type"] == test_job["type"]
        
        # Check general job structure
        for job in data:
            assert "id" in job
            assert "title" in job
            assert "companyId" in job
            assert str(job["companyId"]) == str(test_company["_id"])


def test_get_jobs_by_company_not_found(client):
    """Test getting jobs for non-existent company"""
    # Try to get jobs for non-existent company
    random_id = str(ObjectId())
    response = client.get(f"/api/companies/{random_id}/jobs")

    # Check response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data
    assert "not found" in data["error"].lower()


def test_get_jobs_by_company_invalid_id(client):
    """Test getting jobs with invalid company ID"""
    response = client.get("/api/companies/invalid-id/jobs")
    
    # Should handle invalid ObjectId gracefully
    assert response.status_code in [400, 404]
    data = json.loads(response.data)
    assert "error" in data