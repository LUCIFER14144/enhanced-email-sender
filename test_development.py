"""
Development test script to verify environment setup and core functionality.
Run this after setting up the development environment to ensure everything is working.
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env.development
def load_env():
    with open('.env.development') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

# Test functions
def test_database_connection():
    """Test database connection"""
    import psycopg2
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT')
        )
        conn.close()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def test_api_endpoints():
    """Test core API endpoints"""
    base_url = f"http://localhost:{os.getenv('PORT')}"
    endpoints = {
        'health': '/',
        'login': '/token',
        'users': '/admin/users',
    }
    
    results = []
    for name, path in endpoints.items():
        try:
            response = requests.get(f"{base_url}{path}")
            results.append({
                'endpoint': name,
                'status': response.status_code,
                'success': response.status_code < 400
            })
            logger.info(f"{'✅' if response.status_code < 400 else '❌'} {name}: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ {name} test failed: {e}")
            results.append({
                'endpoint': name,
                'status': None,
                'success': False,
                'error': str(e)
            })
    
    return all(r['success'] for r in results)

def test_admin_login():
    """Test admin login"""
    try:
        response = requests.post(
            f"http://localhost:{os.getenv('PORT')}/token",
            data={
                'username': 'admin',
                'password': os.getenv('ADMIN_DEFAULT_PASSWORD')
            }
        )
        success = response.status_code == 200
        logger.info(f"{'✅' if success else '❌'} Admin login test")
        return success
    except Exception as e:
        logger.error(f"❌ Admin login test failed: {e}")
        return False

def test_email_sending():
    """Test email sending with test SMTP"""
    import smtplib
    from email.mime.text import MIMEText
    
    try:
        msg = MIMEText('Test email from development environment')
        msg['Subject'] = 'Test Email'
        msg['From'] = os.getenv('SMTP_FROM_EMAIL')
        msg['To'] = os.getenv('TEST_USER_EMAIL')
        
        with smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT'))) as server:
            server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
            server.send_message(msg)
            
        logger.info("✅ Email sending test successful")
        return True
    except Exception as e:
        logger.error(f"❌ Email sending test failed: {e}")
        return False

def main():
    """Run all development environment tests"""
    logger.info("Starting development environment tests...")
    
    # Load environment variables
    try:
        load_env()
        logger.info("✅ Environment variables loaded")
    except Exception as e:
        logger.error(f"❌ Failed to load environment variables: {e}")
        return False
    
    # Run tests
    tests = [
        ('Database Connection', test_database_connection),
        ('API Endpoints', test_api_endpoints),
        ('Admin Login', test_admin_login),
        ('Email Sending', test_email_sending)
    ]
    
    results = []
    for name, test_func in tests:
        logger.info(f"\nRunning {name} test...")
        try:
            success = test_func()
            results.append(success)
            logger.info(f"{name} test: {'✅ PASSED' if success else '❌ FAILED'}")
        except Exception as e:
            logger.error(f"❌ {name} test error: {e}")
            results.append(False)
    
    # Summary
    total = len(tests)
    passed = sum(results)
    logger.info(f"\nTest Summary: {passed}/{total} tests passed")
    
    return all(results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)