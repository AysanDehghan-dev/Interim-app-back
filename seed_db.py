import os
import sys
import datetime
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
from passlib.hash import pbkdf2_sha256

# Load environment variables
load_dotenv()

# Connect to MongoDB
# Check if we're in Docker or local environment
import socket


def is_mongo_available(host="mongo", port=27017, timeout=1):
    """Check if MongoDB is available at the given host and port"""
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except (socket.timeout, socket.error):
        return False


# Try to connect to 'mongo' hostname (Docker), otherwise fallback to localhost
if is_mongo_available(host="mongo"):
    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://mongo:27017/interimapp")
else:
    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/interimapp")

print(f"Connecting to MongoDB at {MONGODB_URI}")
client = MongoClient(MONGODB_URI)
db_name = MONGODB_URI.split("/")[-1]
db = client[db_name]

# Clear existing data
db.users.delete_many({})
db.companies.delete_many({})
db.jobs.delete_many({})
db.applications.delete_many({})


# Job types
class JobType:
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    TEMPORARY = "TEMPORARY"
    INTERNSHIP = "INTERNSHIP"


# Application statuses
class ApplicationStatus:
    PENDING = "PENDING"
    REVIEWING = "REVIEWING"
    INTERVIEW = "INTERVIEW"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"


# Create companies
companies = [
    {
        "_id": ObjectId(),
        "name": "TechCorp",
        "industry": "Technologie",
        "description": "Entreprise spécialisée dans le développement de solutions web innovantes. TechCorp est reconnue pour sa culture d'entreprise dynamique et ses avantages compétitifs.",
        "logo": "https://placehold.co/200x200?text=TechCorp",
        "website": "https://techcorp.example.com",
        "email": "contact@techcorp.example.com",
        "password": pbkdf2_sha256.hash("password"),
        "phone": "+33 1 23 45 67 89",
        "address": "50 Rue de l'Innovation",
        "city": "Lyon",
        "country": "France",
        "jobs": [],
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    },
    {
        "_id": ObjectId(),
        "name": "DataInsight",
        "industry": "Analyse de données",
        "description": "Leader dans l'analyse de données et l'intelligence artificielle. DataInsight développe des algorithmes prédictifs pour aider les entreprises à prendre de meilleures décisions basées sur les données.",
        "logo": "https://placehold.co/200x200?text=DataInsight",
        "website": "https://datainsight.example.com",
        "email": "contact@datainsight.example.com",
        "password": pbkdf2_sha256.hash("password"),
        "phone": "+33 1 98 76 54 32",
        "address": "15 Avenue de l'Intelligence",
        "city": "Paris",
        "country": "France",
        "jobs": [],
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    },
]

# Insert companies
company_ids = []
for company in companies:
    result = db.companies.insert_one(company)
    company_ids.append(company["_id"])

# Create users
users = [
    {
        "_id": ObjectId(),
        "first_name": "Jean",
        "last_name": "Dupont",
        "email": "jean.dupont@example.com",
        "password": pbkdf2_sha256.hash("password"),
        "phone": "+33 6 12 34 56 78",
        "address": "25 Rue de Paris",
        "city": "Lyon",
        "country": "France",
        "profile_picture": "https://randomuser.me/api/portraits/men/1.jpg",
        "skills": ["JavaScript", "React", "TypeScript", "Node.js"],
        "experience": [
            {
                "id": str(ObjectId()),
                "title": "Développeur Frontend",
                "company": "TechCorp",
                "location": "Lyon",
                "start_date": datetime.datetime(2020, 1, 1),
                "end_date": datetime.datetime(2022, 12, 31),
                "current": False,
                "description": "Développement d'applications web avec React et TypeScript.",
            }
        ],
        "education": [
            {
                "id": str(ObjectId()),
                "institution": "Université de Lyon",
                "degree": "Master",
                "field": "Informatique",
                "start_date": datetime.datetime(2015, 9, 1),
                "end_date": datetime.datetime(2020, 6, 30),
                "current": False,
                "description": "Spécialisation en développement web et applications mobiles.",
            }
        ],
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    },
    {
        "_id": ObjectId(),
        "first_name": "Marie",
        "last_name": "Laurent",
        "email": "marie.laurent@example.com",
        "password": pbkdf2_sha256.hash("password"),
        "phone": "+33 6 98 76 54 32",
        "address": "10 Avenue Victor Hugo",
        "city": "Paris",
        "country": "France",
        "profile_picture": "https://randomuser.me/api/portraits/women/1.jpg",
        "skills": ["Python", "Data Analysis", "SQL", "Machine Learning"],
        "experience": [
            {
                "id": str(ObjectId()),
                "title": "Data Scientist",
                "company": "DataInsight",
                "location": "Paris",
                "start_date": datetime.datetime(2019, 3, 1),
                "end_date": datetime.datetime(2023, 2, 28),
                "current": False,
                "description": "Analyse de données et création de modèles prédictifs.",
            }
        ],
        "education": [
            {
                "id": str(ObjectId()),
                "institution": "École Polytechnique",
                "degree": "Ingénieur",
                "field": "Science des données",
                "start_date": datetime.datetime(2014, 9, 1),
                "end_date": datetime.datetime(2019, 6, 30),
                "current": False,
                "description": "Spécialisation en data science et intelligence artificielle.",
            }
        ],
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    },
]

# Insert users
user_ids = []
for user in users:
    result = db.users.insert_one(user)
    user_ids.append(user["_id"])

# Create jobs
jobs = [
    {
        "_id": ObjectId(),
        "title": "Développeur Frontend React",
        "company_id": companies[0]["_id"],
        "description": "Nous recherchons un développeur Frontend React expérimenté pour rejoindre notre équipe. Vous serez responsable du développement d'applications web interactives pour nos clients. Vous travaillerez en collaboration avec notre équipe de designers UX et nos développeurs backend pour créer des expériences utilisateur exceptionnelles.",
        "requirements": [
            "Expérience de 3 ans minimum avec React et TypeScript",
            "Maîtrise de HTML5, CSS3 et JavaScript ES6+",
            "Expérience avec les outils de gestion de version comme Git",
            "Connaissance de Redux ou Context API pour la gestion d'état",
            "Expérience avec les tests unitaires (Jest, React Testing Library)",
        ],
        "location": "Lyon, France",
        "type": JobType.FULL_TIME,
        "salary": {"min": 40000, "max": 55000, "currency": "EUR"},
        "start_date": datetime.datetime.utcnow(),
        "applications": [],
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    },
    {
        "_id": ObjectId(),
        "title": "Data Scientist",
        "company_id": companies[1]["_id"],
        "description": "Rejoignez notre équipe d'analyse de données pour travailler sur des projets innovants. Vous serez chargé de concevoir et mettre en œuvre des modèles de machine learning, d'analyser les données pour en extraire des insights pertinents, et de présenter vos résultats à différentes parties prenantes.",
        "requirements": [
            "Master ou PhD en statistiques, mathématiques ou informatique",
            "Expérience pratique en machine learning et en data mining",
            "Maîtrise de Python et des bibliothèques de data science (Pandas, NumPy, Scikit-learn)",
            "Connaissance approfondie des bases de données SQL et NoSQL",
            "Excellentes capacités d'analyse et de communication",
        ],
        "location": "Paris, France",
        "type": JobType.CONTRACT,
        "salary": {"min": 45000, "max": 60000, "currency": "EUR"},
        "start_date": datetime.datetime.utcnow(),
        "applications": [],
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    },
    {
        "_id": ObjectId(),
        "title": "Développeur Backend Node.js",
        "company_id": companies[0]["_id"],
        "description": "Nous recherchons un développeur Backend Node.js pour renforcer notre équipe technique. Vous serez responsable du développement et de la maintenance de notre infrastructure serveur, de l'optimisation des performances et de l'implémentation de nouvelles fonctionnalités.",
        "requirements": [
            "Expérience significative avec Node.js et frameworks comme Express ou NestJS",
            "Maîtrise des bases de données MongoDB et des requêtes complexes",
            "Connaissance approfondie de Git et des workflows de développement",
            "Expérience dans la conception et l'implémentation d'API RESTful",
            "Capacité à travailler de manière autonome et à résoudre des problèmes complexes",
        ],
        "location": "Lyon, France",
        "type": JobType.FULL_TIME,
        "salary": {"min": 42000, "max": 58000, "currency": "EUR"},
        "start_date": datetime.datetime.utcnow(),
        "applications": [],
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    },
    {
        "_id": ObjectId(),
        "title": "UI/UX Designer",
        "company_id": companies[1]["_id"],
        "description": "Nous recherchons un designer UI/UX créatif pour concevoir des interfaces utilisateur intuitives et esthétiques. Vous travaillerez en étroite collaboration avec notre équipe de développeurs pour donner vie à vos designs.",
        "requirements": [
            "Portfolio démontrant d'excellentes compétences en design d'interface",
            "Maîtrise des outils de design (Figma, Adobe XD, Sketch)",
            "Expérience dans la conduite de recherches utilisateurs et de tests d'utilisabilité",
            "Connaissance des principes d'accessibilité et de responsive design",
            "Capacité à communiquer et défendre vos choix de design",
        ],
        "location": "Paris, France",
        "type": JobType.PART_TIME,
        "salary": {"min": 30000, "max": 40000, "currency": "EUR"},
        "start_date": datetime.datetime.utcnow(),
        "applications": [],
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    },
]

# Insert jobs
job_ids = []
for job in jobs:
    result = db.jobs.insert_one(job)
    job_id = job["_id"]
    job_ids.append(job_id)

    # Update company with job reference
    company_id = job["company_id"]
    db.companies.update_one({"_id": company_id}, {"$push": {"jobs": job_id}})

# Create applications
applications = [
    {
        "_id": ObjectId(),
        "job_id": jobs[0]["_id"],
        "user_id": users[1]["_id"],
        "status": ApplicationStatus.PENDING,
        "cover_letter": "Je suis très intéressé par ce poste car j'ai une solide expérience en développement frontend et je souhaite rejoindre une entreprise innovante comme la vôtre.",
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    },
    {
        "_id": ObjectId(),
        "job_id": jobs[1]["_id"],
        "user_id": users[0]["_id"],
        "status": ApplicationStatus.REVIEWING,
        "cover_letter": "Avec mon expérience en développement et mon intérêt pour la data science, je pense être un bon candidat pour ce poste. Je suis impatient de pouvoir contribuer à vos projets innovants.",
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
    },
]

# Insert applications
for application in applications:
    result = db.applications.insert_one(application)
    application_id = application["_id"]

    # Update job with application reference
    job_id = application["job_id"]
    db.jobs.update_one({"_id": job_id}, {"$push": {"applications": application_id}})

print("Database seeded successfully!")
print(f"Created {len(companies)} companies")
print(f"Created {len(users)} users")
print(f"Created {len(jobs)} jobs")
print(f"Created {len(applications)} applications")
