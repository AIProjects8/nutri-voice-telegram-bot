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

def get_db() -> Generator:
    """Dependency injection for database access"""
    try:
        yield db
    except PyMongoError as e:
        print(f"MongoDB connection error: {e}")
        client.close()
        raise


def init_db():
    """Initialize MongoDB database with collections and indexes"""
    print("Starting MongoDB initialization...")

    required_collections = {'meals', 'symptoms', 'users'}
    existing_collections = set(db.list_collection_names())
    
    # Create missing collections
    for col in required_collections - existing_collections:
        db.create_collection(col)
        print(f"Created collection: {col}")
        
    # Create indexes with error handling
    try:
        result1 = db.meals.create_index([("userId", 1)])
        print(f"Created ingredients userId index: {result1}")
        
        result2 = db.meals.create_index([("timestamp", 1)])
        print(f"Created ingredients timestamp index: {result2}")
        
        result3 = db.symptoms.create_index([("userId", 1)])
        print(f"Created symptoms userId index: {result3}")
        
        result4 = db.symptoms.create_index([("timestamp", 1)])
        print(f"Created symptoms timestamp index: {result4}")
        
        result5 = db.users.create_index([("userId", 1)], unique=True)
        print(f"Created users userId index: {result5}")
        
        # Verify indexes were created
        print("Ingredients indexes:", db.ingredients.index_information())
        print("Symptoms indexes:", db.symptoms.index_information())
        print("Users indexes:", db.users.index_information())
        
    except Exception as e:
        print(f"Error creating indexes: {e}")
    
    print("MongoDB initialization complete")


# Create MongoDB client and database instance
client = MongoClient(get_database_uri())
db = client.get_database()