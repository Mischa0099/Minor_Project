# backend/app.py
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv

# local import - db.py should provide 'db' (SQLAlchemy) and an optional 'init_mongo' helper
from db import db

# Load environment variables from .env (if present)
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')

# Ensure instance directory exists and use an absolute sqlite path to avoid relative-path issues
basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(basedir, 'instance')
try:
    os.makedirs(instance_dir, exist_ok=True)
except Exception as e:
    print('Warning: could not create instance directory:', e)

default_db_path = os.path.join(instance_dir, 'database.db')
db_uri_env = os.getenv('DATABASE_URI', '')
if db_uri_env:
    db_uri = db_uri_env
else:
    # sqlite requires absolute path; convert backslashes on Windows
    db_path_abs = os.path.abspath(default_db_path)
    db_path_uri = db_path_abs.replace('\\', '/')
    db_uri = f"sqlite:///{db_path_uri}"

# Try to touch the DB file so permissions errors show early
try:
    open(default_db_path, 'a').close()
except Exception as e:
    print('Warning: could not create sqlite database file:', e)

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy (SQLite backend)
db.init_app(app)

# initialize other extensions (these are harmless if DB init failed earlier)
jwt = JWTManager(app)
CORS(app)

# Run lightweight schema helpers at startup as well (even when not __main__)
try:
    from db import ensure_profile_response_style, ensure_conversations_schema
    with app.app_context():
        try:
            ensure_profile_response_style(app)
            ensure_conversations_schema(app)
        except Exception as e:
            print('Startup schema check failed:', e)
except Exception as e:
    print('Could not import/run schema helpers at startup:', e)

# Register blueprints (wrap in try/except to avoid import-time crashes)
try:
    from routes.auth_routes import auth_bp
    from routes.user_routes import user_bp
    from routes.chat_routes import chat_bp
    # admin_bp might not exist in all versions; ignore if missing
    try:
        from routes.admin_routes import admin_bp
    except Exception:
        admin_bp = None

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    if admin_bp:
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
except Exception as e:
    print('Warning: could not register some blueprints at import time:', e)

# simple health-check
@app.route('/ping', methods=['GET'])
def ping():
    return 'pong', 200

# Prefetch models optional section (keeps existing behavior)
if os.getenv('PREFETCH_MODELS', '0') in ('1', 'true', 'yes'):
    try:
        import threading
        from routes.chat_routes import ensure_models_loaded

        def _prefetch():
            with app.app_context():
                try:
                    ensure_models_loaded()
                    print('Model prefetch completed')
                except Exception as e:
                    print('Model prefetch failed:', e)

        t = threading.Thread(target=_prefetch, daemon=True)
        t.start()
    except Exception as e:
        print('PREFETCH_MODELS requested but failed to start prefetch thread:', e)

if __name__ == '__main__':
    # create SQL tables and run lightweight schema fixes for existing SQLite DBs
    with app.app_context():
        try:
            # run small migration helpers to add missing columns/tables if needed
            from db import ensure_profile_response_style, ensure_conversations_schema
            ensure_profile_response_style(app)
            ensure_conversations_schema(app)
        except Exception as e:
            print('Schema migration helper failed:', e)
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)