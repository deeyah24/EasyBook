"""
BACKEND TESTS - Test backend business logic, validation, and edge cases
"""
import pytest
from datetime import date, time, datetime
from app.models.user import User
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.availability import Availability
from app.tests.conftest import get_token


class TestBackendValidation:
    """Tests for backend validation and business logic"""

    def test_appointment_conflict_detection(self, client, db, service, customer_user,
                                             provider_user, availability):
        token = get_token(client, 'customer@test.com', 'password123')
        payload = {
            'service_id': service.id,
            'appointment_date': '2025-12-08',
            'start_time': '09:00',
        }
        resp1 = client.post('/api/appointments',
                            headers={'Authorization': f'Bearer {token}'}, json=payload)
        assert resp1.status_code == 201

        # Second booking at same time should conflict
        resp2 = client.post('/api/appointments',
                            headers={'Authorization': f'Bearer {token}'}, json=payload)
        assert resp2.status_code == 409

    def test_review_requires_completed_appointment(self, client, db, appointment, customer_user):
        # appointment fixture is 'confirmed', not 'completed'
        token = get_token(client, 'customer@test.com', 'password123')
        resp = client.post('/api/reviews',
                           headers={'Authorization': f'Bearer {token}'},
                           json={'appointment_id': appointment.id, 'rating': 5})
        assert resp.status_code == 400

    def test_review_rating_bounds(self, client, db, service, customer_user, provider_user):
        # Create a completed appointment
        appt = Appointment(
            service_id=service.id,
            customer_id=customer_user.id,
            provider_id=provider_user.id,
            appointment_date=date(2025, 11, 10),
            start_time=time(10, 0),
            end_time=time(10, 30),
            status='completed',
            total_price=50.00,
        )
        db.session.add(appt)
        db.session.commit()

        token = get_token(client, 'customer@test.com', 'password123')
        # Rating of 6 is invalid
        resp = client.post('/api/reviews',
                           headers={'Authorization': f'Bearer {token}'},
                           json={'appointment_id': appt.id, 'rating': 6})
        assert resp.status_code == 400

        # Rating of 0 is invalid
        resp = client.post('/api/reviews',
                           headers={'Authorization': f'Bearer {token}'},
                           json={'appointment_id': appt.id, 'rating': 0})
        assert resp.status_code == 400

    def test_review_valid_rating(self, client, db, service, customer_user, provider_user):
        appt = Appointment(
            service_id=service.id,
            customer_id=customer_user.id,
            provider_id=provider_user.id,
            appointment_date=date(2025, 11, 11),
            start_time=time(11, 0),
            end_time=time(11, 30),
            status='completed',
            total_price=50.00,
        )
        db.session.add(appt)
        db.session.commit()

        token = get_token(client, 'customer@test.com', 'password123')
        resp = client.post('/api/reviews',
                           headers={'Authorization': f'Bearer {token}'},
                           json={'appointment_id': appt.id, 'rating': 5, 'comment': 'Excellent!'})
        assert resp.status_code == 201
        assert resp.get_json()['rating'] == 5

    def test_customer_cannot_update_others_appointment(self, client, db, appointment):
        # Register a different customer
        client.post('/api/auth/register', json={
            'name': 'Other', 'email': 'other@test.com', 'password': 'pass123', 'role': 'customer'
        })
        token = get_token(client, 'other@test.com', 'pass123')
        resp = client.put(f'/api/appointments/{appointment.id}',
                          headers={'Authorization': f'Bearer {token}'},
                          json={'status': 'cancelled'})
        assert resp.status_code == 403

    def test_service_slots_returns_empty_without_availability(self, client, db, service):
        resp = client.get(f'/api/services/{service.id}/slots?date=2025-12-08')
        assert resp.status_code == 200
        assert resp.get_json()['slots'] == []

    def test_service_slots_with_availability(self, client, db, service, availability):
        # Monday = 2025-12-08
        resp = client.get(f'/api/services/{service.id}/slots?date=2025-12-08')
        assert resp.status_code == 200
        slots = resp.get_json()['slots']
        assert len(slots) > 0
        # All slots initially available
        assert all(s['available'] for s in slots)

    def test_service_slots_missing_date(self, client, db, service):
        resp = client.get(f'/api/services/{service.id}/slots')
        assert resp.status_code == 400

    def test_service_slots_invalid_date_format(self, client, db, service):
        resp = client.get(f'/api/services/{service.id}/slots?date=not-a-date')
        assert resp.status_code == 400

    def test_provider_cannot_modify_other_provider_service(self, client, db, service):
        # Create second provider
        client.post('/api/auth/register', json={
            'name': 'Other Provider', 'email': 'other_provider@test.com',
            'password': 'pass123', 'role': 'provider'
        })
        token = get_token(client, 'other_provider@test.com', 'pass123')
        resp = client.put(f'/api/services/{service.id}',
                          headers={'Authorization': f'Bearer {token}'},
                          json={'price': 999})
        assert resp.status_code == 403

    def test_availability_upsert(self, client, db, provider_user):
        token = get_token(client, 'provider@test.com', 'password123')
        # Create
        resp1 = client.post('/api/providers/availability',
                            headers={'Authorization': f'Bearer {token}'},
                            json={'day_of_week': 2, 'start_time': '09:00', 'end_time': '17:00'})
        assert resp1.status_code == 201

        # Update (upsert same day)
        resp2 = client.post('/api/providers/availability',
                            headers={'Authorization': f'Bearer {token}'},
                            json={'day_of_week': 2, 'start_time': '10:00', 'end_time': '18:00'})
        assert resp2.status_code == 201
        assert resp2.get_json()['start_time'] == '10:00'

    def test_inactive_service_cannot_be_booked(self, client, db, service, customer_user):
        service.is_active = False
        db.session.commit()

        token = get_token(client, 'customer@test.com', 'password123')
        resp = client.post('/api/appointments',
                           headers={'Authorization': f'Bearer {token}'},
                           json={
                               'service_id': service.id,
                               'appointment_date': '2025-12-08',
                               'start_time': '09:00',
                           })
        assert resp.status_code == 400

    def test_appointment_status_transitions(self, client, db, appointment, provider_user):
        token = get_token(client, 'provider@test.com', 'password123')

        resp = client.put(f'/api/appointments/{appointment.id}',
                          headers={'Authorization': f'Bearer {token}'},
                          json={'status': 'completed'})
        assert resp.status_code == 200
        assert resp.get_json()['status'] == 'completed'


class TestBackendEdgeCases:
    """Edge case tests for backend"""

    def test_register_with_invalid_role_defaults_to_customer(self, client, db):
        resp = client.post('/api/auth/register', json={
            'name': 'Hack', 'email': 'hack@test.com',
            'password': 'pass', 'role': 'admin'
        })
        assert resp.status_code == 201
        assert resp.get_json()['user']['role'] == 'customer'

    def test_service_price_is_float_in_response(self, client, db, service):
        resp = client.get(f'/api/services/{service.id}')
        assert isinstance(resp.get_json()['price'], float)

    def test_pagination_services(self, client, db, provider_user, category):
        # Create multiple services
        for i in range(15):
            from app.models.service import Service as Svc
            s = Svc(provider_id=provider_user.id, category_id=category.id,
                    name=f'Service {i}', price=10+i, duration_minutes=30)
            db.session.add(s)
        db.session.commit()

        resp = client.get('/api/services?page=1&per_page=5')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['services']) <= 5
        assert data['pages'] > 1
