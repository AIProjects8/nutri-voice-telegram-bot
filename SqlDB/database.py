from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from .models import Base

load_dotenv()

POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'nutri_voice')
DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}'

engine = create_engine(DATABASE_URL)

def init_db():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # TODO: It's very primitive way to check if the database is initialized.
    # If you modified something into the database then remove docker container
    # with command: `docker compose down -v`
    if not existing_tables:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    else:
        print("Database tables already exist")

def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close() 