from app.routes.auth import auth_bp
from app.routes.jobs import jobs_bp
from app.routes.companies import companies_bp
from app.routes.users import users_bp

__all__ = ["auth_bp", "jobs_bp", "companies_bp", "users_bp"]
