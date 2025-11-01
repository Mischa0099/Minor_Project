#!/usr/bin/env python
"""Quick test to check if backend routes are accessible"""
import requests
import sys

BASE_URL = "http://localhost:5000"

def test_endpoint(path, method="GET", data=None):
    try:
        if method == "GET":
            r = requests.get(f"{BASE_URL}{path}", timeout=2)
        elif method == "POST":
            r = requests.post(f"{BASE_URL}{path}", json=data, timeout=2)
        return r.status_code, r.text
    except requests.exceptions.ConnectionError:
        return None, "❌ Connection Error - Backend not running on port 5000"
    except Exception as e:
        return None, f"❌ Error: {e}"

print("=" * 50)
print("Backend Connection Test")
print("=" * 50)

# Test 1: Ping endpoint
print("\n1. Testing /ping endpoint...")
status, response = test_endpoint("/ping")
if status == 200:
    print(f"   ✅ SUCCESS: {status} - {response}")
else:
    print(f"   ❌ FAILED: {status if status else 'Connection Error'} - {response}")
    print("\n   ⚠️ Backend is not running! Start it with: python app.py")
    sys.exit(1)

# Test 2: Routes list
print("\n2. Testing /api/routes endpoint...")
status, response = test_endpoint("/api/routes")
if status == 200:
    print(f"   ✅ SUCCESS: Routes endpoint accessible")
    try:
        import json
        routes_data = json.loads(response)
        print(f"   Total routes: {routes_data.get('total', 0)}")
        print("   Key routes:")
        for route in routes_data.get('routes', [])[:10]:
            if '/api/' in route.get('path', ''):
                print(f"     - {route.get('path')} [{', '.join(route.get('methods', []))}]")
    except:
        pass
else:
    print(f"   ❌ FAILED: {status} - {response}")

# Test 3: Auth register (should return 400 for missing data, not 404)
print("\n3. Testing /api/auth/register endpoint...")
status, response = test_endpoint("/api/auth/register", method="POST", data={})
if status == 400:
    print(f"   ✅ SUCCESS: Route exists (returned 400 as expected for empty data)")
elif status == 404:
    print(f"   ❌ FAILED: Route not found (404)")
else:
    print(f"   ⚠️ Unexpected: {status} - {response}")

# Test 4: Auth login (should return 400 for missing data, not 404)
print("\n4. Testing /api/auth/login endpoint...")
status, response = test_endpoint("/api/auth/login", method="POST", data={})
if status == 400 or status == 401:
    print(f"   ✅ SUCCESS: Route exists (returned {status} as expected)")
elif status == 404:
    print(f"   ❌ FAILED: Route not found (404)")
else:
    print(f"   ⚠️ Unexpected: {status} - {response}")

print("\n" + "=" * 50)
print("Test Complete!")
print("=" * 50)
print("\n💡 If all tests pass, backend is working correctly.")
print("💡 If you see 404 errors, check:")
print("   1. Backend is running: python app.py")
print("   2. No errors in backend console")
print("   3. Routes are registered (check /api/routes)")

