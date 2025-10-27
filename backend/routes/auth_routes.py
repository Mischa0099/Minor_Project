from flask import Blueprint, request, jsonify
from db import db
from models import User, Profile

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 400

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('DB commit failed during user registration:', e)
        return jsonify({'message': 'Registration failed (db error)'}), 500

    # Create profile for the user with default response_style
    try:
        profile = Profile(user_id=user.id, response_style='concise')
        db.session.add(profile)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Non-fatal: user exists; return success but log
        print('Failed to create profile on registration:', e)

    return jsonify({'message': 'User registered successfully'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Ensure the user has a profile (create if missing)
    if not user.profile:
        try:
            profile = Profile(user_id=user.id)
            db.session.add(profile)
            db.session.commit()
        except Exception as e:
            # non-fatal: continue and return token even if profile creation fails
            print('Failed to create profile on login:', e)

    token = user.generate_token()
    return jsonify({'token': token}), 200
