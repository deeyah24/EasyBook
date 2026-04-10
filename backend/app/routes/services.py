from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.service import Service
from app.models.user import User

services_bp = Blueprint('services', __name__)


@services_bp.route('', methods=['GET'])
def get_services():
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    query = Service.query.filter_by(is_active=True)

    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(Service.name.ilike(f'%{search}%'))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'services': [s.to_dict() for s in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
    }), 200


@services_bp.route('/<int:service_id>', methods=['GET'])
def get_service(service_id):
    service = Service.query.get_or_404(service_id)
    return jsonify(service.to_dict()), 200


@services_bp.route('', methods=['POST'])
@jwt_required()
def create_service():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    if user.role not in ['provider', 'admin']:
        return jsonify({'error': 'Only providers can create services'}), 403

    data = request.get_json()
    required = ['name', 'price', 'duration_minutes']
    for field in required:
        if data.get(field) is None:
            return jsonify({'error': f'{field} is required'}), 400

    service = Service(
        provider_id=user_id,
        category_id=data.get('category_id'),
        name=data['name'],
        description=data.get('description'),
        duration_minutes=int(data['duration_minutes']),
        price=float(data['price']),
        max_capacity=data.get('max_capacity', 1),
        location=data.get('location'),
    )
    db.session.add(service)
    db.session.commit()
    return jsonify(service.to_dict()), 201


@services_bp.route('/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_service(service_id):
    user_id = int(get_jwt_identity())
    service = Service.query.get_or_404(service_id)

    user = User.query.get(user_id)
    if service.provider_id != user_id and user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    updatable = ['name', 'description', 'duration_minutes', 'price', 'max_capacity', 'location', 'is_active', 'category_id']
    for field in updatable:
        if field in data:
            setattr(service, field, data[field])

    db.session.commit()
    return jsonify(service.to_dict()), 200


@services_bp.route('/<int:service_id>', methods=['DELETE'])
@jwt_required()
def delete_service(service_id):
    user_id = int(get_jwt_identity())
    service = Service.query.get_or_404(service_id)

    user = User.query.get(user_id)
    if service.provider_id != user_id and user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    service.is_active = False
    db.session.commit()
    return jsonify({'message': 'Service deactivated'}), 200


@services_bp.route('/<int:service_id>/slots', methods=['GET'])
def get_available_slots(service_id):
    from datetime import datetime, timedelta, date as date_type
    from app.models.appointment import Appointment
    from app.models.availability import Availability

    service = Service.query.get_or_404(service_id)
    date_str = request.args.get('date')

    if not date_str:
        return jsonify({'error': 'date parameter required (YYYY-MM-DD)'}), 400

    try:
        requested_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    day_of_week = requested_date.weekday()  # 0=Mon

    availability = Availability.query.filter_by(
        provider_id=service.provider_id,
        day_of_week=day_of_week,
        is_active=True
    ).first()

    if not availability:
        return jsonify({'slots': []}), 200

    # Generate slots
    existing = Appointment.query.filter_by(
        service_id=service_id,
        appointment_date=requested_date,
    ).filter(Appointment.status.in_(['pending', 'confirmed'])).all()

    booked_times = {a.start_time for a in existing}
    slots = []
    current = datetime.combine(requested_date, availability.start_time)
    end = datetime.combine(requested_date, availability.end_time)
    duration = timedelta(minutes=service.duration_minutes)

    while current + duration <= end:
        slot_time = current.time()
        slots.append({
            'time': slot_time.strftime('%H:%M'),
            'available': slot_time not in booked_times
        })
        current += duration

    return jsonify({'slots': slots}), 200
