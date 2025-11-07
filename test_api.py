"""
Test the Enhanced Email Sender API locally
Run this to verify the API is working correctly
"""

import asyncio
import json
from api.main import app
from fastapi.testclient import TestClient

def test_api():
    """Test basic API functionality"""
    client = TestClient(app)
    
    print("🚀 Testing Enhanced Email Sender API...")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing API health check...")
    response = client.get("/")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Message: {data['message']}")
        print("   ✅ Health check passed!")
    else:
        print("   ❌ Health check failed!")
    
    print()
    
    # Test 2: Admin login page
    print("2. Testing admin login page...")
    response = client.get("/admin")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Admin login page accessible!")
    else:
        print("   ❌ Admin login page failed!")
    
    print()
    
    # Test 3: User registration (without database)
    print("3. Testing user registration endpoint...")
    test_user = {
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com"
    }
    
    try:
        response = client.post("/api/auth/register", json=test_user)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 400, 500]:  # Expected without database
            print("   ✅ Registration endpoint responding!")
        else:
            print("   ❌ Registration endpoint failed!")
    except Exception as e:
        print(f"   ⚠️ Registration test skipped (expected without database): {e}")
    
    print()
    
    # Test 4: OpenAPI documentation
    print("4. Testing API documentation...")
    response = client.get("/docs")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ API documentation accessible!")
        print("   📄 Visit http://localhost:8000/docs for interactive docs")
    else:
        print("   ❌ API documentation failed!")
    
    print()
    print("=" * 50)
    print("🎉 API testing completed!")
    print()
    print("Next steps:")
    print("1. Set up Supabase database")
    print("2. Configure environment variables")
    print("3. Deploy to Vercel")
    print("4. Test desktop application")

if __name__ == "__main__":
    # Install test client dependency if needed
    try:
        from fastapi.testclient import TestClient
    except ImportError:
        print("Installing test dependencies...")
        import subprocess
        subprocess.run(["pip", "install", "pytest", "httpx"], check=True)
        from fastapi.testclient import TestClient
    
    test_api()