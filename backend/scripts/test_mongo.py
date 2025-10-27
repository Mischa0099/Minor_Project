# backend/scripts/test_mongo.py
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError

uri = os.getenv('MONGO_URI', 'mongodb://127.0.0.1:27017')
db_name = os.getenv('MONGO_DB_NAME', 'minor_project')

print("Trying to connect to Mongo at:", uri)
try:
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    # triggers actual connection check
    server_info = client.server_info()
    print("Mongo server info:", server_info.get('version'))
    db = client[db_name]
    print("Mongo DB object available for:", db_name)
    # list collections (may be empty)
    print("Collections:", db.list_collection_names())
    client.close()
    print("Mongo connection successful")
except PyMongoError as e:
    print("Mongo connection failed:", type(e).__name__, e)