from pymongo import MongoClient
from config import Config
import sys

client = None
db = None

def init_db():
    global client, db
    try:
        client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        # Test the connection
        client.admin.command('ping')
        db = client.get_database()
        print("MongoDB connected successfully")
        return db
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        print("Please ensure MongoDB is running on", Config.MONGO_URI)
        print("You can start MongoDB by running: mongod")
        sys.exit(1)

def get_db():
    global db
    if db is None:
        db = init_db()
    return db

def close_db():
    global client
    if client:
        client.close()
