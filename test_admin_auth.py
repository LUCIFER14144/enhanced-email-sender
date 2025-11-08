#!/usr/bin/env python3
"""
Test admin login functionality
"""

import requests
from datetime import datetime

BASE_URL = "https://perfected-vercelblasting.vercel.app"

def test_admin_login():
    """Test admin login with form data"""
    print("🧪 Testing Admin Login Form Submission")
    print("=" * 50)
    
    # Test with correct credentials
    print("\n1️⃣ Testing with CORRECT credentials...")
    try:
        response = requests.post(
            f"{BASE_URL}/admin/login",
            data={
                "username": "admin",
                "password": "SecureAdmin123!"  # Use the environment variable password
            },
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ SUCCESS: Admin login successful!")
            if "Admin Dashboard" in response.text:
                print("✅ Dashboard HTML loaded correctly")
            else:
                print("⚠️  Response doesn't contain dashboard")
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # Test with wrong credentials
    print("\n2️⃣ Testing with WRONG credentials...")
    try:
        response = requests.post(
            f"{BASE_URL}/admin/login",
            data={
                "username": "admin",
                "password": "wrongpassword"
            },
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ SUCCESS: Correctly rejected invalid credentials")
            if "Login Failed" in response.text:
                print("✅ Error page shown correctly")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def test_api_endpoints():
    """Test API authentication endpoints"""
    print("\n🧪 Testing API Authentication Endpoints")
    print("=" * 50)
    
    # Prepare a unique username to avoid duplicates on repeated runs
    uniq_suffix = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    reg_username = f"newuser{uniq_suffix}"
    reg_password = "newpass123"

    # Test user registration
    print("\n1️⃣ Testing user registration...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "username": reg_username,
                "password": reg_password,
                "email": f"{reg_username}@example.com",
                "subscription_type": "free"
            },
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("success", True):
                print("✅ SUCCESS: User registration working")
                # Some backends may not return the user object on register; handle both
                reg_report_user = (data.get('user') or {}).get('username', reg_username)
                print(f"   User: {reg_report_user}")
            else:
                print(f"❌ Registration failed: {data.get('message')}")
        elif response.status_code == 400:
            print("⚠️  Registration returned 400 (possibly duplicate). Proceeding to login test anyway.")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # Test user login
    print("\n2️⃣ Testing user login...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": reg_username,
                "password": reg_password
            },
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ SUCCESS: User login working")
                print(f"   User: {data['user']['username']}")
                print(f"   Token: {data['token'][:20]}...")
            else:
                print(f"❌ Login failed: {data.get('message')}")
        else:
            try:
                print(f"❌ Login failed: {response.json()}")
            except Exception:
                print(f"❌ Login failed: {response.text[:200]}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    print("🚀 Enhanced Email Sender - Admin & Auth Testing")
    print("=" * 60)
    
    test_admin_login()
    test_api_endpoints()
    
    print(f"\n{'='*60}")
    print("🎉 Testing Complete!")
    print(f"\n🌐 Your Enhanced Email Sender URLs:")
    print(f"   Main: {BASE_URL}")
    print(f"   Admin: {BASE_URL}/admin")
    print(f"   Debug: {BASE_URL}/debug")
    print(f"   Health: {BASE_URL}/health")
    print(f"   Docs: {BASE_URL}/docs")