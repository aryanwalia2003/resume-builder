"""
src/db.py
---------
MongoDB Connection Manager.
Implements the Singleton pattern to ensure we only create one connection pool.
"""

from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase
from src.config import Config


class Database:
    _client: MongoClient | None = None
    _db: MongoDatabase | None = None

    @classmethod
    def connect(cls) -> None:
        if cls._client is not None:
            return

        config = Config.get_instance()
        uri = config.DB_URI
        print(f"Connecting to MongoDB at {uri}...")
        
        # Connect with serverSelectionTimeoutMS so it fails fast if local DB isn't running
        cls._client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        
        # Extract database name from URI, defaulting to 'resume-builder'
        db_name = uri.split("/")[-1].split("?")[0]
        if not db_name:
            db_name = "resume-builder"
            
        cls._db = cls._client[db_name]
        
        # Ping to verify connection
        cls._client.admin.command('ping')
        print("Successfully connected to MongoDB.")

    @classmethod
    def get_db(cls) -> MongoDatabase:
        """Returns the active database instance. Creates connection if it doesn't exist."""
        if cls._db is None:
            cls.connect()
        return cls._db

    @classmethod
    def close(cls) -> None:
        """Closes the MongoDB connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._db = None
            print("MongoDB connection closed.")
