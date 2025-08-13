import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .base import Base

# Get database path - use the existing db.sqlite3 in project root
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'db.sqlite3')
DATABASE_URL = f'sqlite:///{DATABASE_PATH}'

engine = create_engine(DATABASE_URL, echo=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

def get_session():
    """Get a new database session"""
    return Session()