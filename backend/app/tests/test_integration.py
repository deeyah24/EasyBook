"""
INTEGRATION TESTS - Test API endpoints end-to-end
"""
import pytest
import json
from app.tests.conftest import get_token


class TestAuthIntegration:
    """Integration tests for authentication endpoints"""

    def test_register_customer(self, client, db):
        resp = client.post('/api/auth/register', json={
            'name': 'New User', 'email': 'new@example.com',
            'password': 'pass1234', 'role': 'customer'
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert 'token' in data
        assert data['user']['role'] == 'customer'

    def test_register_provider(self, client, db):
        resp = client.post('/api/auth/register', json={
            'name': 'Dr Smith', 'email': 'drsmith@example.com',
            'password': 'pass1234', 'role': 'provider'
        })
        assert resp.status_code == 201
        assert resp.get_json()['user']['role'] == 'provider'

    def test_register_duplicate_email(self, client, db, customer_user):
        resp = client.post('/api/auth/register', json={
            'name': 'Dupe', 'email': 'customer@test.com', 'password': 'pass'
        })
        assert resp.status_code == 409

    def test_register_missing_fields(self, client, db):
        resp = client.post('/api/auth/register', json={'name': 'No Email'})
        assert resp.status_code == 400

    def test_login_success(self, client, db, customer_user):
        resp = client.post('/api/auth/login', json={
            'email': 'customer@test.com', 'password': 'password123'
        })
        assert resp.status_code == 200
        assert 'token' in resp.get_json()

    def test_login_wrong_password(self, client, db, customer_user):
        resp = client.post('/api/auth/login', json={
            'email': 'customer@test.com', 'password': 'wrongpass'
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client, db):
        resp = client.post('/api/auth/login', json={
            'email': 'nobody@test.com', 'password': 'pass'
        })
        assert resp.status_code == 401

    def test_get_me(self, client, db, customer_user):
        token = get_token(client, 'customer@test.com', 'password123')
        resp = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 200
        assert resp.get_json()['email'] == 'customer@test.com'

    def test_get_me_no_token(self, client, db):
        resp = client.get('/api/auth/me')
        assert resp.status_code == 401

    def test_update_me(self, client, db, customer_user):
        token = get_token(client, 'customer@test.com', 'password123')
        resp = client.put('/api/auth/me',
                          headers={'Authorization': f'Bearer {token}'},
                          json={'name': 'Updated Name', 'phone': '9999999999'})
        assert resp.status_code == 200
        assert resp.get_json()['name'] == 'Updated Name'


class TestServicesIntegration:
    """Integration tests for services endpoints"""

    def test_list_services(self, client, db, service):
        resp = client.get('/api/services')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'services' in data
        assert len(data['services']) >= 1

    def test_get_service_by_id(self, client, db, service):
        resp = client.get(f'/api/services/{service.id}')
        assert resp.status_code == 200
        assert resp.get_json()['name'] == 'General Checkup'

    def test_get_nonexistent_service(self, client, db):
        resp = client.get('/api/services/99999')
        assert resp.status_code == 404

    def test_create_service_as_provider(self, client, db, provider_user, category):
        token = get_token(client, 'provider@test.com', 'password123')
        resp = client.post('/api/services',
                           headers={'Authorization': f'Bearer {token}'},
                           json={
                               'name': 'New Service', 'price': 75.0,
                               'duration_minutes': 45, 'category_id': category.id
                           })
        assert resp.status_code == 201
        assert resp.get_json()['name'] == 'New Service'

    def test_create_service_as_customer_forbidden(self, client, db, customer_user):
        token = get_token(client, 'customer@test.com', 'password123')
        resp = client.post('/api/services',
                           headers={'Authorization': f'Bearer {token}'},
                           json={'name': 'Svc', 'price': 10, 'duration_minutes': 30})
        assert resp.status_code == 403

    def test_update_service(self, client, db, service, provider_user):
        token = get_token(client, 'provider@test.com', 'password123')
        resp = client.put(f'/api/services/{service.id}',
                          headers={'Authorization': f'Bearer {token}'},
                          json={'price': 75.0, 'description': 'Updated desc'})
        assert resp.status_code == 200
        assert resp.get_json()['price'] == 75.0

    def test_delete_service(self, client, db, service, provider_user):
        token = get_token(client, 'provider@test.com', 'password123')
        resp = client.delete(f'/api/services/{service.id}',
                             headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 200

    def test_filter_services_by_category(self, client, db, service, category):
        resp = client.get(f'/api/services?category_id={category.id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert all(s['category_id'] == category.id for s in data['services'])

    def test_search_services(self, client, db, service):
        resp = client.get('/api/services?search=Checkup')
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['services']) >= 1


class TestAppointmentsIntegration:
    """Integration tests for appointments endpoints"""

    def test_create_appointment(self, client, db, service, customer_user, availability):
        token = get_token(client, 'customer@test.com', 'password123')
        resp = client.post('/api/appointments',
                           headers={'Authorization': f'Bearer {token}'},
                           json={
                               'service_id': service.id,
                               'appointment_date': '2025-12-08',  # Monday
                               'start_time': '09:00',
                               'notes': 'First visit'
                           })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['status'] == 'pending'
        assert data['start_time'] == '09:00'

    def test_create_appointment_missing_fields(self, client, db, customer_user):
        token = get_token(client, 'customer@test.com', 'password123')
        resp = client.post('/api/appointments',
                           headers={'Authorization': f'Bearer {token}'},
                           json={'service_id': 1})
        assert resp.status_code == 400

    def test_get_my_appointments(self, client, db, appointment, customer_user):
        token = get_token(client, 'customer@test.com', 'password123')
        resp = client.get('/api/appointments',
                          headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_cancel_appointment(self, client, db, appointment, customer_user):
        token = get_token(client, 'customer@test.com', 'password123')
        resp = client.put(f'/api/appointments/{appointment.id}',
                          headers={'Authorization': f'Bearer {token}'},
                          json={'status': 'cancelled'})
        assert resp.status_code == 200
        assert resp.get_json()['status'] == 'cancelled'

    def test_provider_confirm_appointment(self, client, db, appointment, provider_user):
        token = get_token(client, 'provider@test.com', 'password123')
        resp = client.put(f'/api/appointments/{appointment.id}',
                          headers={'Authorization': f'Bearer {token}'},
                          json={'status': 'confirmed'})
        assert resp.status_code == 200

    def test_get_appointment_unauthorized(self, client, db, appointment, db_extra=None):
        # No token
        resp = client.get(f'/api/appointments/{appointment.id}')
        assert resp.status_code == 401


class TestCategoriesIntegration:
    """Integration tests for categories endpoints"""

    def test_list_categories(self, client, db, category):
        resp = client.get('/api/categories')
        assert resp.status_code == 200
        cats = resp.get_json()
        assert isinstance(cats, list)
        assert len(cats) >= 1

    def test_get_category(self, client, db, category):
        resp = client.get(f'/api/categories/{category.id}')
        assert resp.status_code == 200
        assert resp.get_json()['name'] == 'Medical'

    def test_create_category_as_admin(self, client, db, admin_user):
        token = get_token(client, 'admin@test.com', 'adminpass')
        resp = client.post('/api/categories',
                           headers={'Authorization': f'Bearer {token}'},
                           json={'name': 'Vet', 'description': 'Veterinary', 'icon': '🐾'})
        assert resp.status_code == 201

    def test_create_category_as_customer_forbidden(self, client, db, customer_user):
        token = get_token(client, 'customer@test.com', 'password123')
        resp = client.post('/api/categories',
                           headers={'Authorization': f'Bearer {token}'},
                           json={'name': 'Hacked'})
        assert resp.status_code == 403


class TestProvidersIntegration:
    """Integration tests for providers endpoints"""

    def test_list_providers(self, client, db, provider_user):
        resp = client.get('/api/providers')
        assert resp.status_code == 200
        providers = resp.get_json()
        assert any(p['id'] == provider_user.id for p in providers)

    def test_get_provider_detail(self, client, db, provider_user, service):
        resp = client.get(f'/api/providers/{provider_user.id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'services' in data
        assert 'availability' in data

    def test_set_availability(self, client, db, provider_user):
        token = get_token(client, 'provider@test.com', 'password123')
        resp = client.post('/api/providers/availability',
                           headers={'Authorization': f'Bearer {token}'},
                           json={'day_of_week': 1, 'start_time': '08:00', 'end_time': '16:00'})
        assert resp.status_code == 201

    def test_set_availability_as_customer_forbidden(self, client, db, customer_user):
        token = get_token(client, 'customer@test.com', 'password123')
        resp = client.post('/api/providers/availability',
                           headers={'Authorization': f'Bearer {token}'},
                           json={'day_of_week': 0, 'start_time': '09:00', 'end_time': '17:00'})
        assert resp.status_code == 403


class TestHealthEndpoint:
    """Integration test for health check"""

    def test_health(self, client):
        resp = client.get('/api/health')
        assert resp.status_code == 200
        assert resp.get_json()['status'] == 'ok'
