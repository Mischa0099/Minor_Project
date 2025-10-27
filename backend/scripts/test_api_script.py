import requests
import json
import sys

base_url = 'http://localhost:5000/api'

def safe_post(path, json_data=None, headers=None, timeout=60):
    try:
        return requests.post(f'{base_url}{path}', json=json_data, headers=headers, timeout=timeout)
    except requests.exceptions.RequestException as e:
        print('Request failed:', e)
        sys.exit(1)


# Test Register
register_data = {
    'email': 'test@example.com',
    'password': 'password123'
}
response = safe_post('/auth/register', json_data=register_data, timeout=20)
print('Register Response:', response.status_code, response.text)

# Test Login
login_data = {
    'email': 'test@example.com',
    'password': 'password123'
}
response = safe_post('/auth/login', json_data=login_data, timeout=20)
print('Login Response:', response.status_code, response.text)

if response.status_code == 200:
    token = response.json().get('token')
    headers = {'Authorization': f'Bearer {token}'}

    # Test Profile
    try:
        r = requests.get(f'{base_url}/user/profile', headers=headers, timeout=20)
        print('Profile Response:', r.status_code, r.text)
    except requests.exceptions.RequestException as e:
        print('Profile request failed:', e)

    # Test Chat
    chat_data = {'message': 'Hello, how are you?'}
    try:
        r = requests.post(f'{base_url}/chat/', json=chat_data, headers=headers, timeout=120)
        print('Chat Response:', r.status_code, r.text)
    except requests.exceptions.RequestException as e:
        print('Chat request failed:', e)
