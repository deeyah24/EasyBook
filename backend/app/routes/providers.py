from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.availability import Availability

providers_bp = Blueprint('providers', __name__)


@providers_bp.route('', methods=['GET'])
def get_providers():
    providers = User.query.filter_by(role='provider', is_active=True).all()
    return jsonify([p.to_dict() for p in providers]), 200


@providers_bp.route('/<int:provider_id>', methods=['GET'])
def get_provider(provider_id):
    provider = User.query.filter_by(id=provider_id, role='provider').first_or_404()
    data = provider.to_dict()
    data['services'] = [s.to_dict() for s in provider.services if s.is_active]
    data['availability'] = [a.to_dict() for a in provider.availability if a.is_active]
    return jsonify(data), 200


@providers_bp.route('/availability', methods=['GET'])
@jwt_required()
def get_my_availability():
    user_id = int(get_jwt_identity())
    slots = Availability.query.filter_by(provider_id=user_id).all()
    return jsonify([s.to_dict() for s in slots]), 200


@providers_bp.route('/availability', methods=['POST'])
@jwt_required()
def set_availability():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    if user.role not in ['provider', 'admin']:
        return jsonify({'error': 'Only providers can set availability'}), 403

    data = request.get_json()
    required = ['day_of_week', 'start_time', 'end_time']
    for field in required:
        if data.get(field) is None:
            return jsonify({'error': f'{field} is required'}), 400

    # Upsert availability for day
    existing = Availability.query.filter_by(
        provider_id=user_id,
        day_of_week=data['day_of_week']
    ).first()

    from datetime import datetime
    try:
        start = datetime.strptime(data['start_time'], '%H:%M').time()
        end = datetime.strptime(data['end_time'], '%H:%M').time()
    except ValueError:
        return jsonify({'error': 'Invalid time format, use HH:MM'}), 400

    if existing:
        existing.start_time = start
        existing.end_time = end
        existing.is_active = True
        slot = existing
    else:
        slot = Availability(
            provider_id=user_id,
            day_of_week=data['day_of_week'],
            start_time=start,
            end_time=end,
        )
        db.session.add(slot)

    db.session.commit()
    return jsonify(slot.to_dict()), 201


@providers_bp.route('/availability/<int:slot_id>', methods=['DELETE'])
@jwt_required()
def delete_availability(slot_id):
    user_id = int(get_jwt_identity())
    slot = Availability.query.get_or_404(slot_id)

    if slot.provider_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    slot.is_active = False
    db.session.commit()
    return jsonify({'message': 'Availability removed'}), 200
