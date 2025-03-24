from flask import Blueprint, jsonify, request, current_app
from functools import wraps
import jwt
from datetime import datetime, timedelta
from .models import User, Item
from . import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # The token is expected in the HTTP header "x-access-token"
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token fehlt!'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if current_user is None:
                return jsonify({'message': 'Benutzer nicht gefunden!'}), 401
        except Exception as e:
            return jsonify({'message': 'Ungültiger Token!', 'error': str(e)}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@api_bp.route('/login', methods=['POST'])
@api_bp.route('/login', methods=['POST'])
def api_login():
    auth = request.get_json()
    if not auth or not auth.get('email') or not auth.get('password'):
        return jsonify({'message': 'Fehlende Anmeldedaten'}), 401

    user = User.query.filter_by(email=auth.get('email')).first()
    if not user or not user.check_password(auth.get('password')):
        return jsonify({'message': 'Ungültige Anmeldedaten'}), 401

    try:
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
    except Exception as e:
        return jsonify({'message': 'Fehler beim Generieren des Tokens', 'error': str(e)}), 500

    # Ensure the token is a string (depends on your PyJWT version)
    if isinstance(token, bytes):
        token = token.decode('utf-8')

    return jsonify({'token': token})


@api_bp.route('/items', methods=['GET'])
@token_required
def get_items(current_user):
    """
    Returns all items (for the current user) as JSON.
    This fulfills the read-only API requirement.
    """
    items = Item.query.filter_by(user_id=current_user.id).order_by(Item.created_at.desc()).all()
    items_list = []
    for item in items:
        items_list.append({
            'id': item.id,
            'name': item.name,
            'room': item.room,
            'cost': item.cost,
            'bought_by': item.bought_by,
            'purchase_date': item.purchase_date.isoformat() if item.purchase_date else None,
            'is_new': item.is_new,
            'category': item.category,
            'image_filename': item.image_filename,
            'created_at': item.created_at.isoformat() if item.created_at else None
        })
    return jsonify({'items': items_list})
