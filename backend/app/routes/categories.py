from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.category import Category
from app.models.user import User

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('', methods=['GET'])
def get_categories():
    categories = Category.query.filter_by(is_active=True).all()
    return jsonify([c.to_dict() for c in categories]), 200


@categories_bp.route('/<int:cat_id>', methods=['GET'])
def get_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    return jsonify(cat.to_dict()), 200


@categories_bp.route('', methods=['POST'])
@jwt_required()
def create_category():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    if user.role != 'admin':
        return jsonify({'error': 'Admin only'}), 403

    data = request.get_json()
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400

    cat = Category(
        name=data['name'],
        description=data.get('description'),
        icon=data.get('icon', '📋'),
        color=data.get('color', '#2E86AB'),
    )
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.to_dict()), 201


@categories_bp.route('/<int:cat_id>', methods=['PUT'])
@jwt_required()
def update_category(cat_id):
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    if user.role != 'admin':
        return jsonify({'error': 'Admin only'}), 403

    cat = Category.query.get_or_404(cat_id)
    data = request.get_json()
    for field in ['name', 'description', 'icon', 'color', 'is_active']:
        if field in data:
            setattr(cat, field, data[field])

    db.session.commit()
    return jsonify(cat.to_dict()), 200


@categories_bp.route('/<int:cat_id>', methods=['DELETE'])
@jwt_required()
def delete_category(cat_id):
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    if user.role != 'admin':
        return jsonify({'error': 'Admin only'}), 403

    cat = Category.query.get_or_404(cat_id)
    cat.is_active = False
    db.session.commit()
    return jsonify({'message': 'Category deactivated'}), 200
