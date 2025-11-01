# backend/routes/user_routes.py
from flask import Blueprint, request, jsonify
from db import db
from models import User, Profile
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except Exception:
        pass
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    profile = user.profile
    if not profile:
        return jsonify({'message': 'Profile not found'}), 404

    return jsonify({
        'name': profile.name,
        'age': profile.age,
        'gender': profile.gender,
        'weight': profile.weight,
        'health_conditions': profile.health_conditions,
        'birthmarks': profile.birthmarks,
        # ADDED fields
        'family_medication_history': profile.family_medication_history,
        'previous_medication_history': profile.previous_medication_history,
        # END ADDED fields
        'response_style': profile.response_style if hasattr(profile, 'response_style') else 'concise'
    }), 200

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except Exception:
        pass
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    profile = user.profile
    if not profile:
        profile = Profile(user_id=user_id)
        db.session.add(profile)

    profile.name = data.get('name', profile.name)
    profile.age = data.get('age', profile.age)
    profile.gender = data.get('gender', profile.gender)
    profile.weight = data.get('weight', profile.weight)
    profile.health_conditions = data.get('health_conditions', profile.health_conditions)
    profile.birthmarks = data.get('birthmarks', profile.birthmarks)
    # ADDED fields
    profile.family_medication_history = data.get('family_medication_history', profile.family_medication_history)
    profile.previous_medication_history = data.get('previous_medication_history', profile.previous_medication_history)
    # END ADDED fields
    profile.response_style = data.get('response_style', getattr(profile, 'response_style', 'concise'))

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200