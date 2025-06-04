from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os
from dotenv import load_dotenv
from typing import Generator

load_dotenv()

def get_database_uri():
    """Construct MongoDB connection URI from environment variables"""
    MONGO_USER = os.getenv('MONGO_INITDB_ROOT_USERNAME')
    MONGO_PASS = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB = os.getenv('MONGO_DB', 'nutri_voice')
    
    if not all([MONGO_USER, MONGO_PASS]):
        raise EnvironmentError("MongoDB credentials not configured in .env")
        
    return f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"

# Create MongoDB client and database instance
client = MongoClient(get_database_uri())
db = client.get_database()

def init_db():
    """Initialize MongoDB database with collections and indexes"""
    required_collections = {'ingredients', 'symptoms', 'users'}
    existing_collections = set(db.list_collection_names())
    
    # Create missing collections
    for col in required_collections - existing_collections:
        db.create_collection(col)
        print(f"Created collection: {col}")
        
    # Create indexes
    db.ingredients.create_index([("userId", 1)])
    db.symptoms.create_index([("timestamp", 1)])
    db.users.create_index([("id", 1)], unique=True)
    
    print("MongoDB initialization complete")

def get_db() -> Generator:
    """Dependency injection for database access"""
    try:
        yield db
    except PyMongoError as e:
        print(f"MongoDB connection error: {e}")
        client.close()
        raise
