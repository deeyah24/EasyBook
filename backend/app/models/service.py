from app import db
from datetime import datetime


class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, nullable=False, default=30)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    max_capacity = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    location = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    appointments = db.relationship('Appointment', backref='service', lazy=True)
    reviews = db.relationship('Review', backref='service', lazy=True)

    def average_rating(self):
        if not self.reviews:
            return None
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'category': self.category.to_dict() if self.category else None,
            'provider_id': self.provider_id,
            'provider_name': self.provider.name if self.provider else None,
            'name': self.name,
            'description': self.description,
            'duration_minutes': self.duration_minutes,
            'price': float(self.price),
            'max_capacity': self.max_capacity,
            'is_active': self.is_active,
            'location': self.location,
            'average_rating': self.average_rating(),
            'review_count': len(self.reviews),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
