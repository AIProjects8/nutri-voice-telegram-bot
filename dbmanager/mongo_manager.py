import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import OperationFailure


class MongoDBManager:
    def __init__(
        self, required_collections=None, required_indexes=None, env_path=".env"
    ):
        env_path = Path(env_path)
        load_dotenv(env_path)

        self._client = None
        self._db = None
        self._connected = False
        self._required_collections = required_collections or []
        self._required_indexes = required_indexes or {}

        self.uri = self.get_database_uri()
        self.db_name = os.getenv("MONGO_DB", "nutri_voice")

    def get_database_uri(self):

        MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
        MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
        MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
        MONGO_PORT = os.getenv("MONGO_PORT", "27017")
        MONGO_DB = os.getenv("MONGO_DB", "nutri_voice")

        if not all([MONGO_USER, MONGO_PASS]):
            raise EnvironmentError("MongoDB credentials not configured in .env")

        return f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"

    def _connect(self):
        if not self._connected:
            self._client = MongoClient(self.uri)
            self._db = self._client[self.db_name]
            self._validate_collections_and_indexes()
            self._connected = True

    @property
    def db(self):
        self._connect()
        return self._db

    def _validate_collections_and_indexes(self):
        # Check existence of collections
        for coll, indexes in self._required_indexes.items():
            collection = self._db[coll]
            existing_indexes = collection.index_information()
            for index_spec in indexes:
                index_name = "_".join(
                    [
                        f"{field}_{direction}" for field, direction in index_spec
                    ]  
                )
                # Check existence of indexes
                if index_name not in existing_indexes:
                    collection.create_index(index_spec)
