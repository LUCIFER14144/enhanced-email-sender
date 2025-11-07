#!/usr/bin/env python3
"""
Test script to verify all endpoints are working correctly
"""

import requests
import json

# Your deployed URL
BASE_URL = "https://perfected-vercelblasting.vercel.app"

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """Test an endpoint and return results"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"\n{'='*50}")
        print(f"🧪 Testing: {description}")
        print(f"📡 URL: {url}")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS")
            try:
                result = response.json()
                print(f"📋 Response: {json.dumps(result, indent=2)[:200]}...")
            except:
                print(f"📄 Response: {response.text[:200]}...")
        else:
            print("❌ FAILED")
            print(f"📋 Error: {response.text[:200]}...")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"\n{'='*50}")
        print(f"🧪 Testing: {description}")
        print(f"📡 URL: {url}")
        print(f"❌ EXCEPTION: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Enhanced Email Sender - Endpoint Testing")
    print("=" * 60)
    
    tests = [
        ("/", "GET", None, "Main API Health Check"),
        ("/health", "GET", None, "Detailed Health Check"),
        ("/debug", "GET", None, "Debug Information"),
        ("/test", "GET", None, "Simple Test Endpoint"),
        ("/docs", "GET", None, "API Documentation"),
        ("/admin", "GET", None, "Admin Login Page"),
        ("/api/auth/register", "POST", {
            "username": "testuser123",
            "password": "testpass123",
            "email": "test@example.com",
            "subscription_type": "free"
        }, "User Registration"),
        ("/api/auth/login", "POST", {
            "username": "demo",
            "password": "demo123"
        }, "User Login (Demo Account)"),
    ]
    
    results = []
    for endpoint, method, data, description in tests:
        success = test_endpoint(endpoint, method, data, description)
        results.append((description, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {description}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is working perfectly!")
    else:
        print(f"⚠️  {total - passed} tests failed. Check the errors above.")
    
    print(f"\n🌐 Your live Enhanced Email Sender API:")
    print(f"   Main App: {BASE_URL}")
    print(f"   Admin Dashboard: {BASE_URL}/admin")
    print(f"   API Docs: {BASE_URL}/docs")
    print(f"   Health Check: {BASE_URL}/health")

if __name__ == "__main__":
    main()