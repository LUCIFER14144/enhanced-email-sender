#!/usr/bin/env python3
"""
Final comprehensive test of all Enhanced Email Sender functionality
"""

import requests
import json

BASE_URL = "https://perfected-vercelblasting.vercel.app"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print('='*60)

def print_step(step, description):
    print(f"\n{step} {description}")
    print("-" * 40)

def test_endpoint(method, endpoint, data=None, description=""):
    """Test an endpoint and return detailed results"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            if isinstance(data, dict) and 'username' in data and 'password' in data and endpoint == '/admin/login':
                # Form data for admin login
                response = requests.post(url, data=data, timeout=10)
            else:
                # JSON data for API endpoints
                response = requests.post(url, json=data, timeout=10)
        
        print(f"📡 {method} {endpoint}")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ SUCCESS")
            if 'application/json' in response.headers.get('content-type', ''):
                try:
                    result = response.json()
                    print(f"📋 Response: {json.dumps(result, indent=2)[:300]}...")
                except:
                    print(f"📄 Response: {response.text[:200]}...")
            else:
                if "Dashboard" in response.text:
                    print("📄 Response: Admin Dashboard HTML loaded ✅")
                elif "Login" in response.text:
                    print("📄 Response: Login form HTML loaded ✅")
                else:
                    print(f"📄 Response: {response.text[:100]}...")
            return True
        else:
            print("❌ FAILED")
            print(f"📋 Error: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"📡 {method} {endpoint}")  
        print(f"❌ EXCEPTION: {str(e)}")
        return False

def main():
    print_header("ENHANCED EMAIL SENDER - COMPREHENSIVE TESTING")
    
    # Test 1: Basic API Endpoints
    print_step("1️⃣", "BASIC API ENDPOINTS")
    results = []
    
    basic_tests = [
        ("GET", "/", None, "Main API Health Check"),
        ("GET", "/health", None, "Health Check"),
        ("GET", "/debug", None, "Debug Information"),
        ("GET", "/test", None, "Test Endpoint"),
        ("GET", "/docs", None, "API Documentation"),
    ]
    
    for method, endpoint, data, desc in basic_tests:
        success = test_endpoint(method, endpoint, data, desc)
        results.append((desc, success))
    
    # Test 2: Admin Interface
    print_step("2️⃣", "ADMIN INTERFACE")
    
    # Admin login page
    success = test_endpoint("GET", "/admin", None, "Admin Login Page")
    results.append(("Admin Login Page", success))
    
    # Admin login attempt (we'll try a few common passwords)
    admin_passwords_to_try = [
        "SecureAdmin123!",  # From our environment setup
        "admin123",         # Default fallback
        "your-secure-admin-password"  # From .env.example
    ]
    
    admin_login_success = False
    for password in admin_passwords_to_try:
        print(f"\n🔐 Trying admin login with password: {password[:3]}***")
        success = test_endpoint("POST", "/admin/login", {
            "username": "admin",
            "password": password
        }, f"Admin Login (password: {password[:3]}***)")
        
        if success:
            admin_login_success = True
            break
    
    results.append(("Admin Authentication", admin_login_success))
    
    # Test 3: User Authentication API
    print_step("3️⃣", "USER AUTHENTICATION API")
    
    # User registration
    success = test_endpoint("POST", "/api/auth/register", {
        "username": "testuser456",
        "password": "testpass456",
        "email": "test456@example.com",
        "subscription_type": "free"
    }, "User Registration")
    results.append(("User Registration", success))
    
    # User login with demo account
    success = test_endpoint("POST", "/api/auth/login", {
        "username": "demo",
        "password": "demo123"
    }, "User Login (Demo Account)")
    results.append(("User Login", success))
    
    # Token validation
    success = test_endpoint("GET", "/api/auth/validate", None, "Token Validation")
    results.append(("Token Validation", success))
    
    # Test 4: Results Summary
    print_step("4️⃣", "TEST RESULTS SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed\n")
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {description}")
    
    # Final Status
    print_header("FINAL STATUS")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your Enhanced Email Sender is fully functional!")
    elif passed >= total * 0.8:  # 80% or more
        print("🎯 MOSTLY WORKING! Your Enhanced Email Sender is operational with minor issues.")
    else:
        print("⚠️  PARTIAL FUNCTIONALITY. Some features need attention.")
    
    print(f"\n🌐 Your Live Enhanced Email Sender:")
    print(f"   🏠 Home: {BASE_URL}")
    print(f"   👑 Admin: {BASE_URL}/admin")
    print(f"   💊 Health: {BASE_URL}/health") 
    print(f"   🐛 Debug: {BASE_URL}/debug")
    print(f"   📖 Docs: {BASE_URL}/docs")
    
    print(f"\n🔐 Admin Credentials (try these):")
    print(f"   Username: admin")
    print(f"   Password: SecureAdmin123! (or admin123)")
    
    print(f"\n🎯 Demo User Accounts:")
    print(f"   Username: demo | Password: demo123")
    print(f"   Username: testuser | Password: testpass123")
    
    print(f"\n📱 Next Steps:")
    if admin_login_success:
        print("   ✅ Your admin dashboard is working - you can manage users")
    else:
        print("   🔧 Check admin password in Vercel environment variables")
    
    print("   📱 Update your desktop app with this URL:")
    print(f"      {BASE_URL}")
    print("   🔨 Create desktop executable with PyInstaller")
    print("   🚀 Share the download link with your users!")
    
    print_header("DEPLOYMENT COMPLETE! 🎊")

if __name__ == "__main__":
    main()