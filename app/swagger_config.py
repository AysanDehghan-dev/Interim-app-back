from flask_restx import Api, Resource, fields
from flask import Blueprint

# Create a blueprint for swagger
swagger_bp = Blueprint('api', __name__)

# Configure Swagger
api = Api(
    swagger_bp,
    version='1.0',
    title='InterimApp API',
    description='A simple job search platform API for students',
    doc='/docs/',  # Swagger UI will be available at /api/docs/
    prefix='/api'
)

# Define namespaces (groups)
auth_ns = api.namespace('auth', description='Authentication operations')
users_ns = api.namespace('users', description='User operations')
companies_ns = api.namespace('companies', description='Company operations')
jobs_ns = api.namespace('jobs', description='Job operations')

# Define common models for documentation
user_register_model = api.model('UserRegister', {
    'firstName': fields.String(required=True, description='User first name', example='Jean'),
    'lastName': fields.String(required=True, description='User last name', example='Dupont'),
    'email': fields.String(required=True, description='User email', example='jean.dupont@example.com'),
    'password': fields.String(required=True, description='Password (min 6 chars)', example='password123'),
    'confirmPassword': fields.String(required=True, description='Confirm password', example='password123'),
    'phone': fields.String(description='Phone number', example='+33 6 12 34 56 78'),
    'city': fields.String(description='City', example='Lyon'),
    'country': fields.String(description='Country', example='France'),
})

user_login_model = api.model('UserLogin', {
    'email': fields.String(required=True, description='User email', example='jean.dupont@example.com'),
    'password': fields.String(required=True, description='Password', example='password123'),
})

company_register_model = api.model('CompanyRegister', {
    'name': fields.String(required=True, description='Company name', example='TechCorp'),
    'industry': fields.String(required=True, description='Company industry', example='Technology'),
    'description': fields.String(required=True, description='Company description', example='Leading tech company'),
    'email': fields.String(required=True, description='Company email', example='contact@techcorp.com'),
    'password': fields.String(required=True, description='Password (min 6 chars)', example='password123'),
    'confirmPassword': fields.String(required=True, description='Confirm password', example='password123'),
    'website': fields.String(description='Company website', example='https://techcorp.com'),
    'phone': fields.String(description='Phone number', example='+33 1 23 45 67 89'),
    'address': fields.String(description='Address', example='50 Rue de Innovation'),
    'city': fields.String(description='City', example='Lyon'),
    'country': fields.String(description='Country', example='France'),
})

company_login_model = api.model('CompanyLogin', {
    'email': fields.String(required=True, description='Company email', example='contact@techcorp.com'),
    'password': fields.String(required=True, description='Password', example='password123'),
})

salary_model = api.model('Salary', {
    'min': fields.Integer(required=True, description='Minimum salary', example=40000),
    'max': fields.Integer(required=True, description='Maximum salary', example=55000),
    'currency': fields.String(required=True, description='Currency', example='EUR'),
})

job_create_model = api.model('JobCreate', {
    'title': fields.String(required=True, description='Job title', example='Frontend Developer'),
    'description': fields.String(required=True, description='Job description', example='We are looking for a skilled frontend developer...'),
    'requirements': fields.List(fields.String, required=True, description='Job requirements', 
                               example=['3+ years React experience', 'JavaScript/TypeScript', 'HTML/CSS']),
    'location': fields.String(required=True, description='Job location', example='Lyon, France'),
    'type': fields.String(required=True, description='Job type', 
                         enum=['FULL_TIME', 'PART_TIME', 'CONTRACT', 'TEMPORARY', 'INTERNSHIP'],
                         example='FULL_TIME'),
    'salary': fields.Nested(salary_model, description='Salary information'),
})

job_application_model = api.model('JobApplication', {
    'coverLetter': fields.String(description='Cover letter', example='I am very interested in this position because...'),
})

experience_model = api.model('Experience', {
    'title': fields.String(required=True, description='Job title', example='Frontend Developer'),
    'company': fields.String(required=True, description='Company name', example='TechCorp'),
    'location': fields.String(description='Location', example='Lyon'),
    'startDate': fields.DateTime(required=True, description='Start date', example='2020-01-01T00:00:00Z'),
    'endDate': fields.DateTime(description='End date', example='2022-12-31T00:00:00Z'),
    'current': fields.Boolean(description='Currently working', example=False),
    'description': fields.String(description='Job description', example='Developed web applications using React...'),
})

education_model = api.model('Education', {
    'institution': fields.String(required=True, description='Institution name', example='University of Lyon'),
    'degree': fields.String(required=True, description='Degree', example='Master'),
    'field': fields.String(required=True, description='Field of study', example='Computer Science'),
    'startDate': fields.DateTime(required=True, description='Start date', example='2015-09-01T00:00:00Z'),
    'endDate': fields.DateTime(description='End date', example='2020-06-30T00:00:00Z'),
    'current': fields.Boolean(description='Currently studying', example=False),
    'description': fields.String(description='Description', example='Specialized in web development...'),
})

# Response models
auth_response_model = api.model('AuthResponse', {
    'user': fields.Raw(description='User or company data'),
    'token': fields.String(description='JWT authentication token'),
})

error_model = api.model('Error', {
    'error': fields.String(description='Error type'),
    'message': fields.String(description='Error message'),
})

# Success models
success_model = api.model('Success', {
    'message': fields.String(description='Success message'),
})

pagination_model = api.model('Pagination', {
    'total': fields.Integer(description='Total number of items'),
    'page': fields.Integer(description='Current page'),
    'limit': fields.Integer(description='Items per page'),
    'pages': fields.Integer(description='Total pages'),
})

jobs_response_model = api.model('JobsResponse', {
    'jobs': fields.List(fields.Raw, description='List of jobs'),
    'pagination': fields.Nested(pagination_model),
})