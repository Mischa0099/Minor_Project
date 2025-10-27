import os

# Try to import pymongo; if it's not installed we should fail gracefully so the
# backend can keep running without Mongo support.
_HAS_PYMONGO = True
try:
    from pymongo import MongoClient
except Exception:
    MongoClient = None
    _HAS_PYMONGO = False

USE_MONGO = os.getenv('USE_MONGO', 'false').lower() in ('1', 'true', 'yes') and _HAS_PYMONGO
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
_mongo_client = None
_db = None


def get_mongo_db():
    """Return a pymongo Database instance or None if Mongo is disabled/unavailable."""
    global _mongo_client, _db
    if not USE_MONGO:
        if not _HAS_PYMONGO and os.getenv('USE_MONGO', '0') in ('1', 'true', 'yes'):
            print('WARNING: pymongo not installed; Mongo integration disabled. To enable, run: pip install pymongo')
        return None
    if _db:
        return _db
    try:
        _mongo_client = MongoClient(MONGO_URI)
        _db = _mongo_client.get_database(os.getenv('MONGO_DB', 'minorproject'))
        return _db
    except Exception as e:
        print('Failed to connect to MongoDB:', e)
        return None


def close_mongo():
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None