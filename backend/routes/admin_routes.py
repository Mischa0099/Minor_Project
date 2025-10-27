from flask import Blueprint, request, jsonify, current_app
import os
import yaml
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'response_templates.yaml')

def admin_protect(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Default admin password is '123' if ADMIN_KEY not provided
        admin_key = os.getenv('ADMIN_KEY', '123')
        req_key = request.headers.get('X-ADMIN-KEY') or request.args.get('admin_key')
        if req_key != admin_key:
            return jsonify({'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/recent_chats', methods=['GET'])
@admin_protect
def recent_chats():
    # supports ?source=mongo or ?limit=20
    source = request.args.get('source', 'sql')
    limit = int(request.args.get('limit', 20))
    user_filter = request.args.get('user_id')
    if source == 'mongo':
        try:
            from mongo import get_mongo_db, USE_MONGO
            if not USE_MONGO:
                return jsonify({'message': 'Mongo not enabled'}), 400
            mdb = get_mongo_db()
            docs = list(mdb.chats.find().sort('created_at', -1).limit(limit))
            for d in docs:
                d['_id'] = str(d.get('_id'))
            return jsonify(docs), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500

    # default: SQL
    try:
        from models import ChatHistory
        q = ChatHistory.query
        if user_filter:
            try:
                q = q.filter_by(user_id=int(user_filter))
            except Exception:
                pass
        rows = q.order_by(ChatHistory.created_at.desc()).limit(limit).all()
        out = []
        for r in rows:
            out.append({
                'id': r.id,
                'user_id': r.user_id,
                'user_message': r.user_message,
                'ai_response': r.ai_response,
                'sentiment_label': r.sentiment_label,
                'sentiment_score': r.sentiment_score,
                'created_at': r.created_at.isoformat()
            })
        return jsonify(out), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@admin_bp.route('/templates', methods=['GET', 'PUT'])
@admin_protect
def templates():
    if request.method == 'GET':
        try:
            with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
                return jsonify(yaml.safe_load(f) or {}), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500

    # PUT: replace templates file with provided JSON body
    try:
        data = request.get_json() or {}
        with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
        return jsonify({'message': 'Templates updated'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@admin_bp.route('/alerts', methods=['GET'])
@admin_protect
def alerts():
    """Return recent alerts, optional filter by user_id. Supports ?limit= and ?user_id=.
    """
    try:
        from models import Alert
        limit = int(request.args.get('limit', 50))
        limit = max(1, min(200, limit))
        user_filter = request.args.get('user_id')
        q = Alert.query
        if user_filter:
            try:
                q = q.filter_by(user_id=int(user_filter))
            except Exception:
                pass
        rows = q.order_by(Alert.created_at.desc()).limit(limit).all()
        out = []
        for r in rows:
            out.append({
                'id': r.id,
                'user_id': r.user_id,
                'alert_type': r.alert_type,
                'message': r.message,
                'acknowledged': bool(getattr(r, 'acknowledged', False)),
                'created_at': r.created_at.isoformat() if r.created_at else None,
            })
        return jsonify(out), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
