import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_register_and_login(client):
    # Register
    rv = client.post('/api/auth/register', json={'email': 'a@b.com', 'password': 'pass'})
    assert rv.status_code == 201

    # Duplicate register should fail
    rv = client.post('/api/auth/register', json={'email': 'a@b.com', 'password': 'pass'})
    assert rv.status_code == 400

    # Login
    rv = client.post('/api/auth/login', json={'email': 'a@b.com', 'password': 'pass'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'token' in data
