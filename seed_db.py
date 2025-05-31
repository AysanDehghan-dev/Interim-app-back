# seed.py
"""
Database seeding script using the improved models and validation
"""
import os
import sys
from datetime import datetime, timedelta

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your improved models and utilities
from app.models.user import User
from app.models.company import Company
from app.models.job import Job
from app.models.application import Application
from app.models.enums import JobType, ApplicationStatus
from app.models.exceptions import ValidationError
from app.utils.db import get_db
from config import get_config


def create_app():
    """Create minimal Flask app for database operations"""
    app = Flask(__name__)
    
    # Load configuration
    app_config = get_config()
    app.config.from_object(app_config)
    
    # Initialize database connection
    from pymongo import MongoClient
    from urllib.parse import urlparse
    
    try:
        mongodb_client = MongoClient(
            app.config["MONGODB_URI"],
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
        )
        
        # Test connection
        mongodb_client.admin.command("ping")
        
        # Get database name
        parsed_uri = urlparse(app.config["MONGODB_URI"])
        db_name = parsed_uri.path.lstrip('/') or 'interimapp'
        
        db = mongodb_client[db_name]
        
        # Make available to app
        app.mongodb_client = mongodb_client
        app.db = db
        
        print(f"✅ Connected to MongoDB: {db_name}")
        return app
        
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {str(e)}")
        sys.exit(1)


def clear_database(app):
    """Clear existing data from all collections"""
    with app.app_context():
        db = app.db
        
        collections = ['users', 'companies', 'jobs', 'applications']
        
        for collection in collections:
            count = db[collection].count_documents({})
            if count > 0:
                db[collection].delete_many({})
                print(f"🗑️  Cleared {count} documents from {collection}")
            else:
                print(f"📭 Collection {collection} was already empty")


def create_sample_companies():
    """Create sample companies using the improved Company model"""
    companies_data = [
        {
            "name": "TechCorp",
            "industry": "Technology",
            "description": "Leading software development company specializing in web and mobile applications. We're passionate about creating innovative solutions that make a difference.",
            "logo": "https://placehold.co/200x200/3B82F6/FFFFFF?text=TechCorp",
            "website": "https://techcorp.example.com",
            "email": "contact@techcorp.example.com",
            "password": "SecurePass123",
            "phone": "+33123456789",
            "address": "50 Rue de l'Innovation",
            "city": "Lyon",
            "country": "France",
        },
        {
            "name": "DataInsight",
            "industry": "Data Analytics",
            "description": "Data science and AI company helping businesses make data-driven decisions. We specialize in machine learning and predictive analytics.",
            "logo": "https://placehold.co/200x200/10B981/FFFFFF?text=DataInsight",
            "website": "https://datainsight.example.com", 
            "email": "contact@datainsight.example.com",
            "password": "SecurePass123",
            "phone": "+33987654321",
            "address": "15 Avenue de l'Intelligence",
            "city": "Paris",
            "country": "France",
        },
        {
            "name": "CreativeStudio",
            "industry": "Design",
            "description": "Award-winning design agency creating beautiful and functional user experiences. We work with startups and enterprises worldwide.",
            "logo": "https://placehold.co/200x200/F59E0B/FFFFFF?text=Creative",
            "website": "https://creativestudio.example.com",
            "email": "hello@creativestudio.example.com", 
            "password": "SecurePass123",
            "phone": "+33456789123",
            "address": "25 Boulevard des Arts",
            "city": "Marseille",
            "country": "France",
        }
    ]
    
    created_companies = []
    
    for company_data in companies_data:
        try:
            company_id = Company.create(company_data)
            company = Company.find_by_id(company_id)
            created_companies.append(company)
            print(f"✅ Created company: {company_data['name']}")
            
        except ValidationError as e:
            print(f"❌ Failed to create company {company_data['name']}: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error creating company {company_data['name']}: {str(e)}")
    
    return created_companies


def create_sample_users():
    """Create sample users using the improved User model"""
    users_data = [
        {
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jean.dupont@example.com",
            "password": "SecurePass123",
            "phone": "+33612345678",
            "address": "25 Rue de Paris",
            "city": "Lyon",
            "country": "France",
            "profile_picture": "https://randomuser.me/api/portraits/men/1.jpg",
            "skills": ["JavaScript", "React", "TypeScript", "Node.js", "MongoDB"],
        },
        {
            "first_name": "Marie",
            "last_name": "Laurent", 
            "email": "marie.laurent@example.com",
            "password": "SecurePass123",
            "phone": "+33698765432",
            "address": "10 Avenue Victor Hugo",
            "city": "Paris",
            "country": "France",
            "profile_picture": "https://randomuser.me/api/portraits/women/1.jpg",
            "skills": ["Python", "Data Analysis", "SQL", "Machine Learning", "TensorFlow"],
        },
        {
            "first_name": "Pierre",
            "last_name": "Martin",
            "email": "pierre.martin@example.com", 
            "password": "SecurePass123",
            "phone": "+33655443322",
            "address": "5 Place de la République",
            "city": "Marseille", 
            "country": "France",
            "profile_picture": "https://randomuser.me/api/portraits/men/2.jpg",
            "skills": ["UI/UX Design", "Figma", "Adobe Creative Suite", "Prototyping"],
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        try:
            user_id = User.create(user_data)
            user = User.find_by_id(user_id)
            created_users.append(user)
            print(f"✅ Created user: {user_data['first_name']} {user_data['last_name']}")
            
        except ValidationError as e:
            print(f"❌ Failed to create user {user_data['email']}: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error creating user {user_data['email']}: {str(e)}")
    
    return created_users


def add_user_experience_and_education(users):
    """Add experience and education to users"""
    if len(users) >= 2:
        # Add experience to Jean
        try:
            User.add_experience(users[0]["_id"], {
                "title": "Frontend Developer",
                "company": "TechStart",
                "location": "Lyon, France",
                "start_date": datetime(2020, 1, 1),
                "end_date": datetime(2022, 12, 31),
                "current": False,
                "description": "Developed modern web applications using React and TypeScript."
            })
            
            User.add_education(users[0]["_id"], {
                "school": "Université de Lyon",
                "degree": "Master",
                "field": "Computer Science",
                "start_date": datetime(2015, 9, 1),
                "end_date": datetime(2020, 6, 30),
                "current": False,
                "description": "Specialized in web development and mobile applications."
            })
            
            print("✅ Added experience and education for Jean")
            
        except Exception as e:
            print(f"❌ Failed to add experience for Jean: {str(e)}")
        
        # Add experience to Marie
        try:
            User.add_experience(users[1]["_id"], {
                "title": "Data Scientist",
                "company": "DataCorp",
                "location": "Paris, France", 
                "start_date": datetime(2019, 3, 1),
                "end_date": datetime(2023, 2, 28),
                "current": False,
                "description": "Built machine learning models and performed data analysis."
            })
            
            User.add_education(users[1]["_id"], {
                "school": "École Polytechnique",
                "degree": "Engineering Degree",
                "field": "Data Science",
                "start_date": datetime(2014, 9, 1),
                "end_date": datetime(2019, 6, 30),
                "current": False,
                "description": "Specialized in data science and artificial intelligence."
            })
            
            print("✅ Added experience and education for Marie")
            
        except Exception as e:
            print(f"❌ Failed to add experience for Marie: {str(e)}")


def create_sample_jobs(companies):
    """Create sample jobs using the improved Job model"""
    if len(companies) < 2:
        print("❌ Not enough companies to create jobs")
        return []
    
    jobs_data = [
        {
            "title": "Senior React Developer", 
            "company_id": str(companies[0]["_id"]),
            "description": "We're looking for an experienced React developer to join our team. You'll work on cutting-edge web applications and collaborate with our design team to create amazing user experiences.",
            "requirements": [
                "3+ years experience with React and TypeScript",
                "Strong knowledge of HTML5, CSS3, and JavaScript ES6+",
                "Experience with state management (Redux, Context API)",
                "Familiarity with testing frameworks (Jest, React Testing Library)",
                "Good understanding of Git and agile development practices"
            ],
            "location": "Lyon, France",
            "type": JobType.FULL_TIME,
            "start_date": datetime.utcnow() + timedelta(days=30),
        },
        {
            "title": "Data Scientist",
            "company_id": str(companies[1]["_id"]),
            "description": "Join our data science team to work on exciting AI projects. You'll develop machine learning models, analyze large datasets, and help drive data-driven decisions.",
            "requirements": [
                "Master's or PhD in Statistics, Mathematics, or Computer Science",
                "Strong experience with Python and data science libraries",
                "Knowledge of machine learning algorithms and techniques", 
                "Experience with SQL and NoSQL databases",
                "Excellent analytical and communication skills"
            ],
            "location": "Paris, France",
            "type": JobType.CONTRACT,
            "start_date": datetime.utcnow() + timedelta(days=15),
        },
        {
            "title": "Backend Developer",
            "company_id": str(companies[0]["_id"]),
            "description": "We need a skilled backend developer to build robust and scalable server-side applications. You'll work with modern technologies and help architect our platform.",
            "requirements": [
                "Strong experience with Node.js and Express/NestJS",
                "Deep knowledge of MongoDB and database design",
                "Experience with RESTful API design and implementation",
                "Understanding of microservices architecture",
                "Knowledge of containerization (Docker) and cloud platforms"
            ],
            "location": "Lyon, France",
            "type": JobType.FULL_TIME,
            "start_date": datetime.utcnow() + timedelta(days=45),
        },
        {
            "title": "UI/UX Designer",
            "company_id": str(companies[2]["_id"]) if len(companies) > 2 else str(companies[1]["_id"]),
            "description": "Creative UI/UX designer needed to create beautiful and intuitive user interfaces. You'll work closely with our development team to bring designs to life.",
            "requirements": [
                "Strong portfolio showing excellent design skills",
                "Proficiency with design tools (Figma, Adobe XD, Sketch)",
                "Experience with user research and usability testing",
                "Knowledge of accessibility and responsive design principles", 
                "Ability to create and maintain design systems"
            ],
            "location": "Remote",
            "type": JobType.PART_TIME,
            "start_date": datetime.utcnow() + timedelta(days=20),
        }
    ]
    
    created_jobs = []
    
    for job_data in jobs_data:
        try:
            job_id = Job.create(job_data)
            job = Job.find_by_id(job_id)
            created_jobs.append(job)
            
            # Add job reference to company
            Company.add_job(job_data["company_id"], job_id)
            
            print(f"✅ Created job: {job_data['title']}")
            
        except ValidationError as e:
            print(f"❌ Failed to create job {job_data['title']}: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error creating job {job_data['title']}: {str(e)}")
    
    return created_jobs


def create_sample_applications(users, jobs):
    """Create sample applications using the improved Application model"""
    if len(users) < 2 or len(jobs) < 2:
        print("❌ Not enough users or jobs to create applications")
        return []
    
    applications_data = [
        {
            "job_id": str(jobs[0]["_id"]),
            "user_id": str(users[1]["_id"]),  # Marie applying to React job
            "cover_letter": "I'm very interested in this position as I have experience with modern web technologies and I'm looking to transition into frontend development.",
            "status": ApplicationStatus.PENDING,
        },
        {
            "job_id": str(jobs[1]["_id"]),
            "user_id": str(users[0]["_id"]),  # Jean applying to Data Science job
            "cover_letter": "With my development background and growing interest in data science, I believe I could bring a unique perspective to your team.",
            "status": ApplicationStatus.REVIEWING,
        }
    ]
    
    created_applications = []
    
    for app_data in applications_data:
        try:
            application_id = Application.create(app_data)
            application = Application.find_by_id(application_id)
            created_applications.append(application)
            
            # Add application reference to job
            Job.add_application(app_data["job_id"], application_id)
            
            print(f"✅ Created application: {application_id}")
            
        except ValidationError as e:
            print(f"❌ Failed to create application: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error creating application: {str(e)}")
    
    return created_applications


def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    
    # Create Flask app and connect to database
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        clear_database(app)
        
        # Create sample data
        print("\n📊 Creating sample companies...")
        companies = create_sample_companies()
        
        print(f"\n👥 Creating sample users...")
        users = create_sample_users()
        
        print(f"\n📚 Adding experience and education...")
        add_user_experience_and_education(users)
        
        print(f"\n💼 Creating sample jobs...")
        jobs = create_sample_jobs(companies)
        
        print(f"\n📝 Creating sample applications...")
        applications = create_sample_applications(users, jobs)
        
        # Print summary
        print(f"\n🎉 Database seeding completed successfully!")
        print(f"📈 Summary:")
        print(f"   • {len(companies)} companies created")
        print(f"   • {len(users)} users created")
        print(f"   • {len(jobs)} jobs created")
        print(f"   • {len(applications)} applications created")
        
        print(f"\n🔐 Test credentials:")
        print(f"   Companies: contact@techcorp.example.com / SecurePass123")
        print(f"   Users: jean.dupont@example.com / SecurePass123")


if __name__ == "__main__":
    main()