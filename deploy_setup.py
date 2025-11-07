#!/usr/bin/env python3
"""
Setup script for Enhanced Email Sender deployment
This script helps configure Supabase and prepare for Vercel deployment
"""

import requests
import json
import os
import subprocess
import sys
from getpass import getpass

def print_header(title):
    print("\n" + "="*50)
    print(f"🚀 {title}")
    print("="*50)

def print_step(step, description):
    print(f"\n{step} {description}")
    print("-" * 40)

def generate_jwt_secret():
    """Generate a secure JWT secret"""
    import secrets
    import string
    
    # Generate a 32-character random string
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    secret = ''.join(secrets.choice(alphabet) for _ in range(32))
    return secret

def test_supabase_connection(url, anon_key):
    """Test Supabase connection"""
    try:
        headers = {
            'apikey': anon_key,
            'Authorization': f'Bearer {anon_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{url}/rest/v1/", headers=headers, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False

def setup_supabase():
    """Guide user through Supabase setup"""
    print_header("SUPABASE DATABASE SETUP")
    
    print("📋 Follow these steps to set up your Supabase database:")
    print("1. Go to https://supabase.com")
    print("2. Create a new account or sign in")
    print("3. Click 'New Project'")
    print("4. Fill in project details:")
    print("   - Name: enhanced-email-sender")
    print("   - Database Password: [Choose a strong password]")
    print("   - Region: [Select closest to your users]")
    print("5. Wait for project to be created (2-3 minutes)")
    
    input("\n⏸️  Press Enter when your Supabase project is ready...")
    
    print("\n📡 Now let's get your Supabase credentials:")
    print("1. In your Supabase dashboard, go to Settings → API")
    print("2. Copy the following values:")
    
    supabase_url = input("\n🔗 Enter your Project URL (https://xxx.supabase.co): ").strip()
    anon_key = input("🔑 Enter your anon public key: ").strip()
    service_key = getpass("🔐 Enter your service_role key (hidden): ").strip()
    
    # Test connection
    print("\n🧪 Testing Supabase connection...")
    if test_supabase_connection(supabase_url, anon_key):
        print("✅ Supabase connection successful!")
    else:
        print("❌ Supabase connection failed. Please check your credentials.")
        return None
    
    return {
        'SUPABASE_URL': supabase_url,
        'SUPABASE_ANON_KEY': anon_key,
        'SUPABASE_SERVICE_KEY': service_key
    }

def setup_database_schema(supabase_config):
    """Guide user through database schema setup"""
    print_step("📊", "DATABASE SCHEMA SETUP")
    
    print("Now let's set up the database tables:")
    print("1. In your Supabase dashboard, go to SQL Editor")
    print("2. Click 'New Query'")
    print("3. Copy the entire contents of 'database/schema.sql'")
    print("4. Paste it in the SQL Editor")
    print("5. Click 'Run' to execute the schema")
    
    # Read and display the schema
    try:
        with open('database/schema.sql', 'r') as f:
            schema_content = f.read()
        
        print(f"\n📄 Schema file contains {len(schema_content.splitlines())} lines")
        print("✅ Schema file found and ready to copy")
        
        input("\n⏸️  Press Enter when you've successfully run the schema in Supabase...")
        
        # Test if tables were created by trying to query them
        print("\n🧪 Testing database schema...")
        
        headers = {
            'apikey': supabase_config['SUPABASE_ANON_KEY'],
            'Authorization': f'Bearer {supabase_config["SUPABASE_ANON_KEY"]}',
            'Content-Type': 'application/json'
        }
        
        # Test users table
        response = requests.get(
            f"{supabase_config['SUPABASE_URL']}/rest/v1/users?select=count",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Database schema setup successful!")
            return True
        else:
            print("⚠️  Could not verify schema. Please ensure all tables were created.")
            return False
            
    except FileNotFoundError:
        print("❌ Schema file not found! Make sure you're in the project directory.")
        return False
    except Exception as e:
        print(f"⚠️  Schema test failed: {str(e)}")
        print("Please verify the schema was created manually in Supabase.")
        return True  # Continue anyway

def setup_environment():
    """Set up environment variables"""
    print_step("⚙️", "ENVIRONMENT CONFIGURATION")
    
    # Get Supabase config
    supabase_config = setup_supabase()
    if not supabase_config:
        print("❌ Supabase setup failed. Please try again.")
        return False
    
    # Setup database schema
    schema_success = setup_database_schema(supabase_config)
    
    # Generate JWT secret
    jwt_secret = generate_jwt_secret()
    print(f"\n🔐 Generated JWT secret: {jwt_secret}")
    
    # Get admin credentials
    print("\n👑 Admin Account Setup:")
    admin_username = input("Enter admin username (default: admin): ").strip() or "admin"
    admin_password = getpass("Enter admin password (hidden): ").strip()
    
    if not admin_password:
        print("❌ Admin password is required!")
        return False
    
    # Create environment config
    env_config = {
        **supabase_config,
        'JWT_SECRET': jwt_secret,
        'ADMIN_USERNAME': admin_username,
        'ADMIN_PASSWORD': admin_password
    }
    
    # Save to .env file for local testing
    print("\n💾 Creating .env file for local development...")
    with open('.env', 'w') as f:
        f.write("# Enhanced Email Sender - Environment Variables\n")
        f.write("# Generated by setup script\n\n")
        for key, value in env_config.items():
            f.write(f"{key}={value}\n")
    
    print("✅ Environment file created!")
    print("📝 Next: Deploy to Vercel with these environment variables")
    
    return env_config

def deploy_to_vercel(env_config):
    """Deploy to Vercel"""
    print_step("🚀", "VERCEL DEPLOYMENT")
    
    print("Now let's deploy to Vercel:")
    print("1. Make sure you're logged into Vercel CLI")
    print("2. We'll deploy your project and set environment variables")
    
    # Check if logged in to Vercel
    try:
        result = subprocess.run(['vercel', 'whoami'], capture_output=True, text=True)
        if result.returncode != 0:
            print("\n🔐 Please log in to Vercel:")
            subprocess.run(['vercel', 'login'])
    except FileNotFoundError:
        print("❌ Vercel CLI not found! Please install it:")
        print("   npm install -g vercel")
        return False
    
    # Deploy project
    print("\n🚀 Deploying to Vercel...")
    print("When prompted:")
    print("- Link to existing project? N")
    print("- Project name: enhanced-email-sender (or your choice)")
    print("- Directory: ./ (current directory)")
    print("- Override settings? N")
    
    input("\n⏸️  Press Enter to start Vercel deployment...")
    
    try:
        # Run vercel deploy
        result = subprocess.run(['vercel', '--prod'], check=False)
        
        if result.returncode == 0:
            print("\n✅ Deployment successful!")
            
            # Set environment variables
            print("\n⚙️ Setting environment variables...")
            
            for key, value in env_config.items():
                cmd = ['vercel', 'env', 'add', key, 'production']
                print(f"Setting {key}...")
                
                # Use subprocess with input
                process = subprocess.run(cmd, input=value, text=True, capture_output=True)
                
                if process.returncode == 0:
                    print(f"✅ {key} set successfully")
                else:
                    print(f"⚠️  Failed to set {key}: {process.stderr}")
            
            print("\n🎉 Deployment complete!")
            print("📱 Your app should be live at the URL shown above")
            return True
        else:
            print("❌ Deployment failed. Please check the output above.")
            return False
            
    except Exception as e:
        print(f"❌ Deployment error: {str(e)}")
        return False

def test_deployment():
    """Test the deployed application"""
    print_step("🧪", "DEPLOYMENT TESTING")
    
    app_url = input("\nEnter your Vercel app URL (https://your-app.vercel.app): ").strip()
    
    print(f"\n🔍 Testing {app_url}...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{app_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health: {data.get('message')}")
        else:
            print(f"⚠️  API Health returned {response.status_code}")
    except Exception as e:
        print(f"❌ API Health test failed: {str(e)}")
    
    # Test admin dashboard
    try:
        response = requests.get(f"{app_url}/admin", timeout=10)
        if response.status_code == 200:
            print("✅ Admin dashboard accessible")
        else:
            print(f"⚠️  Admin dashboard returned {response.status_code}")
    except Exception as e:
        print(f"❌ Admin dashboard test failed: {str(e)}")
    
    print(f"\n🌐 Your Enhanced Email Sender is live at: {app_url}")
    print(f"👑 Admin dashboard: {app_url}/admin")
    print(f"📖 API docs: {app_url}/docs")

def main():
    """Main setup workflow"""
    print_header("ENHANCED EMAIL SENDER - DEPLOYMENT SETUP")
    
    print("🎯 This script will help you:")
    print("   1. Set up Supabase database")
    print("   2. Configure environment variables")
    print("   3. Deploy to Vercel")
    print("   4. Test your deployment")
    
    if input("\n❓ Continue with setup? (y/N): ").lower() != 'y':
        print("Setup cancelled.")
        return
    
    # Check if in correct directory
    if not os.path.exists('api/main.py'):
        print("❌ Please run this script from the project root directory")
        print("   (The directory containing api/, desktop/, etc.)")
        return
    
    # Setup environment
    env_config = setup_environment()
    if not env_config:
        print("❌ Environment setup failed")
        return
    
    # Deploy to Vercel
    deploy_success = deploy_to_vercel(env_config)
    if not deploy_success:
        print("❌ Deployment failed")
        print("💡 You can deploy manually later with: vercel --prod")
        return
    
    # Test deployment
    test_deployment()
    
    print_header("SETUP COMPLETE!")
    print("🎉 Your Enhanced Email Sender is now live!")
    print("\n📋 Next steps:")
    print("   1. Test the admin dashboard")
    print("   2. Create test users")
    print("   3. Update desktop app with your API URL")
    print("   4. Build desktop executable with PyInstaller")
    print("   5. Share download link with users")
    
    print("\n📚 For detailed instructions, see DEPLOYMENT.md")

if __name__ == "__main__":
    main()