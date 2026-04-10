from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app import db
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.user import User

appointments_bp = Blueprint('appointments', __name__)


@appointments_bp.route('', methods=['GET'])
@jwt_required()
def get_appointments():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    if user.role == 'customer':
        query = Appointment.query.filter_by(customer_id=user_id)
    elif user.role == 'provider':
        query = Appointment.query.filter_by(provider_id=user_id)
    else:  # admin
        query = Appointment.query

    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.start_time.desc()).all()
    return jsonify([a.to_dict() for a in appointments]), 200


@appointments_bp.route('/<int:appt_id>', methods=['GET'])
@jwt_required()
def get_appointment(appt_id):
    user_id = int(get_jwt_identity())
    appt = Appointment.query.get_or_404(appt_id)
    user = User.query.get(user_id)

    if appt.customer_id != user_id and appt.provider_id != user_id and user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify(appt.to_dict()), 200


@appointments_bp.route('', methods=['POST'])
@jwt_required()
def create_appointment():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    required = ['service_id', 'appointment_date', 'start_time']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    service = Service.query.get_or_404(data['service_id'])
    if not service.is_active:
        return jsonify({'error': 'Service is not available'}), 400

    try:
        appt_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
    except ValueError:
        return jsonify({'error': 'Invalid date or time format'}), 400

    # Calculate end time
    start_dt = datetime.combine(appt_date, start_time)
    end_dt = start_dt + timedelta(minutes=service.duration_minutes)
    end_time = end_dt.time()

    # Check for conflicts
    conflict = Appointment.query.filter_by(
        service_id=service.id,
        appointment_date=appt_date,
        start_time=start_time,
    ).filter(Appointment.status.in_(['pending', 'confirmed'])).first()

    if conflict:
        return jsonify({'error': 'This time slot is already booked'}), 409

    appt = Appointment(
        service_id=service.id,
        customer_id=user_id,
        provider_id=service.provider_id,
        appointment_date=appt_date,
        start_time=start_time,
        end_time=end_time,
        notes=data.get('notes'),
        total_price=service.price,
        status='pending',
    )
    db.session.add(appt)
    db.session.commit()
    return jsonify(appt.to_dict()), 201


@appointments_bp.route('/<int:appt_id>', methods=['PUT'])
@jwt_required()
def update_appointment(appt_id):
    user_id = int(get_jwt_identity())
    appt = Appointment.query.get_or_404(appt_id)
    user = User.query.get(user_id)
    data = request.get_json()

    # Customers can only cancel their own
    if user.role == 'customer':
        if appt.customer_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        if 'status' in data and data['status'] != 'cancelled':
            return jsonify({'error': 'Customers can only cancel appointments'}), 403

    # Providers can confirm/complete/no_show their appointments
    elif user.role == 'provider':
        if appt.provider_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403

    allowed_statuses = ['pending', 'confirmed', 'cancelled', 'completed', 'no_show']
    if 'status' in data:
        if data['status'] not in allowed_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        appt.status = data['status']

    if 'notes' in data:
        appt.notes = data['notes']

    db.session.commit()
    return jsonify(appt.to_dict()), 200


@appointments_bp.route('/<int:appt_id>', methods=['DELETE'])
@jwt_required()
def delete_appointment(appt_id):
    user_id = int(get_jwt_identity())
    appt = Appointment.query.get_or_404(appt_id)
    user = User.query.get(user_id)

    if appt.customer_id != user_id and user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    appt.status = 'cancelled'
    db.session.commit()
    return jsonify({'message': 'Appointment cancelled'}), 200
