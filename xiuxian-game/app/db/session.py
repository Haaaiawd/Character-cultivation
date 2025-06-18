# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session # Session is imported for type hinting
from app.core.config import settings

# Ensure SQLALCHEMY_DATABASE_URI is a string for create_engine
if settings.SQLALCHEMY_DATABASE_URI is None:
    raise ValueError("SQLALCHEMY_DATABASE_URI is not set. Please check your .env file or environment variables.")

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db: Session = SessionLocal() # Add type hint for db
    try:
        yield db
    finally:
        db.close()

# Function to create tables (for initial setup, can be called from main.py or a script)
# This should ideally be handled by Alembic migrations in a full app.
def init_db():
    # Import all models here before calling create_all
    # This ensures they are registered with SQLAlchemy's metadata
    # from app.models.base import Base # Corrected import if Base is directly in base.py
    # from app.models import User, Character # etc. if they are exposed in app.models.__init__

    # The following line is commented out as per subtask instructions.
    # Table creation will be handled later or by Alembic.
    # Base.metadata.create_all(bind=engine)
    pass
