from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.availability import Review
from app.models.appointment import Appointment
from app.models.user import User

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('', methods=['GET'])
def get_reviews():
    service_id = request.args.get('service_id', type=int)
    query = Review.query
    if service_id:
        query = query.filter_by(service_id=service_id)
    reviews = query.order_by(Review.created_at.desc()).all()
    return jsonify([r.to_dict() for r in reviews]), 200


@reviews_bp.route('', methods=['POST'])
@jwt_required()
def create_review():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    required = ['appointment_id', 'rating']
    for field in required:
        if data.get(field) is None:
            return jsonify({'error': f'{field} is required'}), 400

    appt = Appointment.query.get_or_404(data['appointment_id'])

    if appt.customer_id != user_id:
        return jsonify({'error': 'You can only review your own appointments'}), 403

    if appt.status != 'completed':
        return jsonify({'error': 'Can only review completed appointments'}), 400

    if appt.review:
        return jsonify({'error': 'Already reviewed'}), 409

    rating = int(data['rating'])
    if not 1 <= rating <= 5:
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400

    review = Review(
        appointment_id=appt.id,
        customer_id=user_id,
        service_id=appt.service_id,
        rating=rating,
        comment=data.get('comment'),
    )
    db.session.add(review)
    db.session.commit()
    return jsonify(review.to_dict()), 201


@reviews_bp.route('/<int:review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    user_id = int(get_jwt_identity())
    review = Review.query.get_or_404(review_id)

    if review.customer_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    if 'rating' in data:
        rating = int(data['rating'])
        if not 1 <= rating <= 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        review.rating = rating
    if 'comment' in data:
        review.comment = data['comment']

    db.session.commit()
    return jsonify(review.to_dict()), 200


@reviews_bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    review = Review.query.get_or_404(review_id)

    if review.customer_id != user_id and user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted'}), 200
