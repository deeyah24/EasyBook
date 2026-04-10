import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app import create_app, db as _db
from app.models.user import User
from app.models.category import Category
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.availability import Availability, Review
from datetime import date, time, timedelta


TEST_CONFIG = {
    'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL', 'sqlite:///:memory:'),
    'JWT_SECRET_KEY': 'test-secret',
    'WTF_CSRF_ENABLED': False,
}


@pytest.fixture(scope='session')
def app():
    application = create_app(TEST_CONFIG)
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def customer_user(db):
    user = User(name='Test Customer', email='customer@test.com', role='customer', phone='1234567890')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def provider_user(db):
    user = User(name='Test Provider', email='provider@test.com', role='provider', phone='0987654321')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_user(db):
    user = User(name='Admin User', email='admin@test.com', role='admin')
    user.set_password('admin123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def category(db):
    cat = Category(name='Medical', description='Healthcare', icon='hospital', color='#2E86AB')
    db.session.add(cat)
    db.session.commit()
    return cat


@pytest.fixture
def service(db, provider_user, category):
    svc = Service(
        provider_id=provider_user.id,
        category_id=category.id,
        name='General Consultation',
        description='30 min consultation',
        duration_minutes=30,
        price=50.00,
        location='Room 101',
    )
    db.session.add(svc)
    db.session.commit()
    return svc


@pytest.fixture
def availability(db, provider_user):
    avail = Availability(
        provider_id=provider_user.id,
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(17, 0),
    )
    db.session.add(avail)
    db.session.commit()
    return avail


@pytest.fixture
def appointment(db, service, customer_user, provider_user):
    tomorrow = date.today() + timedelta(days=1)
    appt = Appointment(
        service_id=service.id,
        customer_id=customer_user.id,
        provider_id=provider_user.id,
        appointment_date=tomorrow,
        start_time=time(10, 0),
        end_time=time(10, 30),
        status='confirmed',
        total_price=50.00,
    )
    db.session.add(appt)
    db.session.commit()
    return appt


@pytest.fixture
def completed_appointment(db, service, customer_user, provider_user):
    yesterday = date.today() - timedelta(days=1)
    appt = Appointment(
        service_id=service.id,
        customer_id=customer_user.id,
        provider_id=provider_user.id,
        appointment_date=yesterday,
        start_time=time(10, 0),
        end_time=time(10, 30),
        status='completed',
        total_price=50.00,
    )
    db.session.add(appt)
    db.session.commit()
    return appt


@pytest.fixture
def db_session(db):
    """Alias for db fixture used in unit tests."""
    return db


def get_token(client, email, password):
    resp = client.post('/api/auth/login', json={'email': email, 'password': password})
    data = resp.get_json()
    return data.get('token')


def auth_headers(token):
    return {'Authorization': f'Bearer {token}'}
