#!/usr/bin/env python
"""Quick script to check if routes are registered"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    
    print("=" * 60)
    print("BACKEND ROUTE CHECK")
    print("=" * 60)
    
    # Check if app was created
    if app is None:
        print("❌ ERROR: App is None!")
        sys.exit(1)
    
    print(f"\n✅ App created successfully")
    print(f"✅ App name: {app.name}")
    
    # List all routes
    print("\n📋 Registered Routes:")
    print("-" * 60)
    
    api_routes = []
    for rule in app.url_map.iter_rules():
        if 'api' in str(rule) or 'ping' in str(rule) or 'routes' in str(rule):
            methods = list(rule.methods - {'HEAD', 'OPTIONS'})
            api_routes.append((str(rule), methods))
            print(f"  {str(rule):<40} {', '.join(methods)}")
    
    # Check critical routes
    print("\n🔍 Critical Route Check:")
    print("-" * 60)
    
    critical_routes = [
        ('/api/auth/login', ['POST']),
        ('/api/auth/register', ['POST']),
        ('/api/user/profile', ['GET', 'PUT']),
        ('/api/chat/', ['POST']),
        ('/ping', ['GET'])
    ]
    
    all_routes = {str(rule): list(rule.methods) for rule in app.url_map.iter_rules()}
    
    for route_path, expected_methods in critical_routes:
        if route_path in all_routes:
            methods = [m for m in all_routes[route_path] if m not in ['HEAD', 'OPTIONS']]
            if any(m in expected_methods for m in methods):
                print(f"  ✅ {route_path:<40} {', '.join(methods)}")
            else:
                print(f"  ⚠️  {route_path:<40} {', '.join(methods)} (expected {', '.join(expected_methods)})")
        else:
            print(f"  ❌ {route_path:<40} NOT FOUND")
    
    print("\n" + "=" * 60)
    print(f"Total API routes found: {len(api_routes)}")
    print("=" * 60)
    
    if len(api_routes) == 0:
        print("\n❌ WARNING: No API routes found! Backend won't work.")
        print("Check for import errors in route files.")
        sys.exit(1)
    else:
        print("\n✅ Routes are registered. Backend should work.")
        print("\n💡 To start backend:")
        print("   python app.py")
        print("\n💡 Then test with:")
        print("   http://localhost:5000/ping")
        print("   http://localhost:5000/api/routes")

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\n💡 Install missing dependencies:")
    print("   pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

