#!/usr/bin/env python3
"""
Test admin login functionality
"""

import requests

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
    
    # Test user registration
    print("\n1️⃣ Testing user registration...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "username": "newuser123",
                "password": "newpass123",
                "email": "newuser@example.com",
                "subscription_type": "free"
            },
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ SUCCESS: User registration working")
                print(f"   User: {data['user']['username']}")
            else:
                print(f"❌ Registration failed: {data.get('message')}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # Test user login
    print("\n2️⃣ Testing user login...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": "demo",
                "password": "demo123"
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