"""
UNIT TESTS - Test individual model logic and helper functions
"""
import pytest
from datetime import date, time
from app.models.user import User
from app.models.category import Category
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.availability import Availability, Review


class TestUserModel:
    """Unit tests for User model"""

    def test_user_creation(self, db):
        user = User(name='John Doe', email='john@example.com', role='customer')
        user.set_password('secret123')
        db.session.add(user)
        db.session.commit()
        assert user.id is not None
        assert user.name == 'John Doe'
        assert user.role == 'customer'

    def test_password_hashing(self, db):
        user = User(name='Jane', email='jane@example.com', role='customer')
        user.set_password('mypassword')
        assert user.check_password('mypassword') is True
        assert user.check_password('wrongpassword') is False

    def test_password_not_stored_plaintext(self, db):
        user = User(name='Bob', email='bob@example.com', role='customer')
        user.set_password('plaintext')
        assert user.password_hash != 'plaintext'

    def test_user_to_dict(self, customer_user):
        d = customer_user.to_dict()
        assert 'id' in d
        assert 'name' in d
        assert 'email' in d
        assert 'password_hash' not in d  # Should not expose hash

    def test_user_default_active(self, db):
        user = User(name='Active', email='active@example.com', role='customer')
        user.set_password('pass')
        db.session.add(user)
        db.session.commit()
        assert user.is_active is True

    def test_unique_email_constraint(self, db, customer_user):
        user2 = User(name='Dupe', email='customer@test.com', role='customer')
        user2.set_password('pass')
        db.session.add(user2)
        with pytest.raises(Exception):
            db.session.commit()


class TestCategoryModel:
    """Unit tests for Category model"""

    def test_category_creation(self, db):
        cat = Category(name='Dental', description='Dental care', icon='🦷', color='#3BB273')
        db.session.add(cat)
        db.session.commit()
        assert cat.id is not None
        assert cat.name == 'Dental'

    def test_category_to_dict(self, category):
        d = category.to_dict()
        assert d['name'] == 'Medical'
        assert 'service_count' in d
        assert d['service_count'] == 0

    def test_category_service_count(self, db, category, service):
        d = category.to_dict()
        assert d['service_count'] == 1

    def test_category_default_active(self, category):
        assert category.is_active is True


class TestServiceModel:
    """Unit tests for Service model"""

    def test_service_creation(self, service):
        assert service.id is not None
        assert service.name == 'General Consultation'
        assert float(service.price) == 50.00

    def test_service_to_dict(self, service):
        d = service.to_dict()
        assert d['name'] == 'General Consultation'
        assert d['price'] == 50.0
        assert d['duration_minutes'] == 30
        assert 'provider_name' in d
        assert 'category' in d

    def test_service_average_rating_no_reviews(self, service):
        assert service.average_rating() is None

    def test_service_average_rating_with_reviews(self, db, service, customer_user, provider_user):
        appt = Appointment(
            service_id=service.id,
            customer_id=customer_user.id,
            provider_id=provider_user.id,
            appointment_date=date(2025, 12, 1),
            start_time=time(9, 0),
            end_time=time(9, 30),
            status='completed',
            total_price=50.00,
        )
        db.session.add(appt)
        db.session.commit()

        review = Review(
            appointment_id=appt.id,
            customer_id=customer_user.id,
            service_id=service.id,
            rating=4,
            comment='Good service',
        )
        db.session.add(review)
        db.session.commit()
        assert service.average_rating() == 4.0


class TestAppointmentModel:
    """Unit tests for Appointment model"""

    def test_appointment_to_dict(self, appointment):
        d = appointment.to_dict()
        assert d['status'] == 'confirmed'
        assert d['start_time'] == '10:00'
        assert d['end_time'] == '10:30'
        assert d['total_price'] == 50.0

    def test_appointment_has_review_false(self, appointment):
        d = appointment.to_dict()
        assert d['has_review'] is False


class TestAvailabilityModel:
    """Unit tests for Availability model"""

    def test_availability_to_dict(self, availability):
        d = availability.to_dict()
        assert d['day_of_week'] == 0
        assert d['day_name'] == 'Monday'
        assert d['start_time'] == '09:00'
        assert d['end_time'] == '17:00'
