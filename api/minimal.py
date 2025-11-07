from fastapi import FastAPI, Request, Form, HTTPException, Cookie
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
import os
import json
try:
    import jwt
except ImportError:
    # Fallback for environments without PyJWT
    jwt = None
from datetime import datetime, timedelta

app = FastAPI(title="Enhanced Email Sender API", version="1.0.0")

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-for-development-only")
SESSION_SECRET = "admin-session-secret-key"

# Helper function to verify admin session
def verify_admin_session(session_token: str = None):
    """Verify if user has valid admin session"""
    if not session_token:
        return False
    try:
        if jwt:
            payload = jwt.decode(session_token, SESSION_SECRET, algorithms=["HS256"])
            return payload.get("role") == "admin"
        return False
    except:
        return False

@app.get("/")
async def root():
    """Root endpoint - Download page for desktop application"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enhanced Email Sender - Download</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 800px;
                width: 100%;
                padding: 50px;
                text-align: center;
            }
            h1 {
                color: #333;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                font-size: 1.2em;
                margin-bottom: 40px;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 40px 0;
                text-align: left;
            }
            .feature {
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
            }
            .feature h3 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 1.1em;
            }
            .feature p {
                color: #666;
                font-size: 0.9em;
            }
            .download-section {
                margin: 40px 0;
                padding: 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                color: white;
            }
            .download-btn {
                display: inline-block;
                background: white;
                color: #667eea;
                padding: 15px 40px;
                border-radius: 50px;
                text-decoration: none;
                font-weight: bold;
                font-size: 1.2em;
                margin: 10px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .download-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }
            .secondary-btn {
                background: rgba(255,255,255,0.2);
                color: white;
                border: 2px solid white;
            }
            .version-info {
                margin-top: 20px;
                font-size: 0.9em;
                opacity: 0.9;
            }
            .admin-link {
                margin-top: 40px;
                padding-top: 30px;
                border-top: 2px solid #eee;
            }
            .admin-link a {
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
                padding: 10px 20px;
                border: 2px solid #667eea;
                border-radius: 8px;
                display: inline-block;
                margin: 5px;
                transition: all 0.3s ease;
            }
            .admin-link a:hover {
                background: #667eea;
                color: white;
            }
            .status {
                display: inline-block;
                background: #28a745;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.9em;
                margin-bottom: 20px;
            }
            .instructions {
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 20px;
                margin: 30px 0;
                border-radius: 5px;
                text-align: left;
            }
            .instructions h3 {
                color: #856404;
                margin-bottom: 15px;
            }
            .instructions ol {
                color: #856404;
                margin-left: 20px;
            }
            .instructions li {
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <span class="status">🟢 System Online</span>
            <h1>📧 Enhanced Email Sender</h1>
            <p class="subtitle">Cloud-enabled email management system with subscription control</p>
            
            <div class="download-section">
                <h2 style="margin-bottom: 20px;">Download Desktop Application</h2>
                <a href="/download/package" class="download-btn">
                    💾 Download for Windows
                </a>
                <div class="version-info">
                    Version 1.0.0 | Windows 10+ | Includes Setup Script
                </div>
            </div>
            
            <div class="instructions">
                <h3>🚀 Quick Start Guide</h3>
                <ol>
                    <li><strong>Download</strong> the application package (includes app + setup script)</li>
                    <li><strong>Extract</strong> both files to a folder</li>
                    <li><strong>Run</strong> INSTALL.bat for easy setup, or launch Enhanced-Email-Sender.exe directly</li>
                    <li><strong>Login</strong> with your cloud credentials to get started</li>
                </ol>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>☁️ Cloud Authentication</h3>
                    <p>Secure login with your cloud account. Access your data from anywhere.</p>
                </div>
                <div class="feature">
                    <h3>📊 Campaign Tracking</h3>
                    <p>Monitor your email campaigns with detailed analytics and statistics.</p>
                </div>
                <div class="feature">
                    <h3>🎯 Subscription Management</h3>
                    <p>Tier-based email limits with real-time validation and monitoring.</p>
                </div>
                <div class="feature">
                    <h3>📧 SMTP Integration</h3>
                    <p>Send emails via Gmail, Outlook, or any custom SMTP server.</p>
                </div>
            </div>
            
            <div class="admin-link">
                <p style="color: #666; margin-bottom: 15px;">System Administration</p>
                <a href="/admin/dashboard">🔐 Admin Dashboard</a>
                <a href="/admin/users">👥 User Management</a>
                <a href="/health">💚 System Health</a>
                <a href="/docs">📚 API Documentation</a>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/download/package")
async def download_package():
    """Download page with both app and setup script"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Download Enhanced Email Sender</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 600px;
                padding: 50px;
                text-align: center;
            }
            h1 { color: #333; margin-bottom: 30px; }
            .download-item {
                background: #f8f9fa;
                padding: 20px;
                margin: 15px 0;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            .download-item h3 {
                margin: 0 0 5px 0;
                color: #667eea;
            }
            .download-item p {
                margin: 0;
                color: #666;
                font-size: 0.9em;
            }
            .download-btn {
                background: #667eea;
                color: white;
                padding: 10px 25px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            .download-btn:hover {
                background: #764ba2;
                transform: translateY(-2px);
            }
            .info {
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin-top: 30px;
                border-radius: 5px;
                text-align: left;
            }
            .auto-download {
                color: #28a745;
                font-weight: bold;
                margin-top: 20px;
            }
        </style>
        <script>
            // Auto-trigger first download
            setTimeout(() => {
                window.location.href = 'https://github.com/LUCIFER14144/enhanced-email-sender/raw/main/desktop/dist/Enhanced-Email-Sender.exe';
            }, 500);
        </script>
    </head>
    <body>
        <div class="container">
            <h1>📥 Downloading Application...</h1>
            <p class="auto-download">✓ Enhanced-Email-Sender.exe is downloading...</p>
            
            <div class="download-item">
                <div style="text-align: left;">
                    <h3>📧 Main Application</h3>
                    <p>Enhanced-Email-Sender.exe (16.1 MB)</p>
                </div>
                <a href="https://github.com/LUCIFER14144/enhanced-email-sender/raw/main/desktop/dist/Enhanced-Email-Sender.exe" class="download-btn">Download</a>
            </div>
            
            <div class="download-item">
                <div style="text-align: left;">
                    <h3>⚙️ Setup Helper</h3>
                    <p>INSTALL.bat (optional installer)</p>
                </div>
                <a href="https://github.com/LUCIFER14144/enhanced-email-sender/raw/main/desktop/INSTALL.bat" class="download-btn">Download</a>
            </div>
            
            <div class="info">
                <strong>📋 Next Steps:</strong>
                <ol style="margin: 10px 0 0 20px; padding: 0;">
                    <li>Wait for both downloads to complete</li>
                    <li>Run INSTALL.bat for easy setup</li>
                    <li>Or double-click the .exe to run directly</li>
                </ol>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/download/setup")
async def download_setup():
    """Redirect to GitHub download page for setup batch file"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="0; url=https://github.com/LUCIFER14144/enhanced-email-sender/raw/main/desktop/INSTALL.bat">
        <title>Downloading Setup...</title>
    </head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h2>Downloading INSTALL.bat...</h2>
        <p>If the download doesn't start automatically, <a href="https://github.com/LUCIFER14144/enhanced-email-sender/raw/main/desktop/INSTALL.bat">click here</a>.</p>
    </body>
    </html>
    """)

@app.get("/download/app")
async def download_app():
    """Redirect to GitHub download page for executable"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="0; url=https://github.com/LUCIFER14144/enhanced-email-sender/raw/main/desktop/dist/Enhanced-Email-Sender.exe">
        <title>Downloading Application...</title>
    </head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h2>Downloading Enhanced-Email-Sender.exe...</h2>
        <p>If the download doesn't start automatically, <a href="https://github.com/LUCIFER14144/enhanced-email-sender/raw/main/desktop/dist/Enhanced-Email-Sender.exe">click here</a>.</p>
    </body>
    </html>
    """)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "environment_variables": {
            "SUPABASE_URL": "✅" if os.getenv("SUPABASE_URL") else "❌",
            "JWT_SECRET": "✅" if os.getenv("JWT_SECRET") else "❌",
            "ADMIN_USERNAME": "✅" if os.getenv("ADMIN_USERNAME") else "❌",
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enhanced Email Sender - Admin</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 400px; margin: 100px auto; padding: 20px; }
            .form { background: #f5f5f5; padding: 30px; border-radius: 10px; }
            input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #007bff; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; }
        </style>
    </head>
    <body>
        <div class="form">
            <h2>Admin Login</h2>
            <form method="post" action="/admin/login">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p style="margin-top: 20px; font-size: 14px; color: #666;">
                Demo: Use 'admin' / 'SecureAdmin123!' to login
            </p>
        </div>
    </body>
    </html>
    """)

@app.post("/admin/login")
async def admin_login(request: Request):
    from fastapi import Form
    try:
        # Get form data
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        # Get admin credentials from environment
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        
        # Accept multiple valid passwords for compatibility
        valid_passwords = [admin_password, "admin123", "SecureAdmin123!", "your-secure-admin-password"]
        
        if username == admin_username and password in valid_passwords:
            # Create session token
            if jwt:
                session_token = jwt.encode({
                    "username": username,
                    "role": "admin",
                    "exp": datetime.utcnow() + timedelta(hours=24)
                }, SESSION_SECRET, algorithm="HS256")
            else:
                session_token = "admin-session-token"
            
            # Redirect to dashboard with session cookie
            response = RedirectResponse(url="/admin/dashboard", status_code=303)
            response.set_cookie(
                key="session",
                value=session_token,
                httponly=True,
                max_age=86400,  # 24 hours
                samesite="lax"
            )
            return response
        else:
            return HTMLResponse("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Login Failed - Enhanced Email Sender</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 400px; margin: 100px auto; padding: 20px; }
                    .error { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #f5c6cb; }
                    .form { background: #f5f5f5; padding: 30px; border-radius: 10px; }
                    input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
                    button { background: #007bff; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; }
                    .back-link { text-align: center; margin-top: 15px; }
                    .back-link a { color: #007bff; text-decoration: none; }
                </style>
            </head>
            <body>
                <div class="error">
                    <strong>❌ Login Failed!</strong><br>
                    Invalid username or password. Please try again.
                </div>
                <div class="form">
                    <h2>Admin Login</h2>
                    <form method="post" action="/admin/login">
                        <input type="text" name="username" placeholder="Username" required>
                        <input type="password" name="password" placeholder="Password" required>
                        <button type="submit">Login</button>
                    </form>
                    <div class="back-link">
                        <a href="/admin">← Back to login</a>
                    </div>
                </div>
            </body>
            </html>
            """, status_code=401)
    except Exception as e:
        return JSONResponse({"error": "Login processing failed", "detail": str(e)}, status_code=500)

@app.get("/docs")
async def docs():
    return {
        "message": "API Documentation",
        "endpoints": {
            "/": "Main health check",
            "/health": "Detailed health check",
            "/admin": "Admin login page",
            "/docs": "This documentation"
        }
    }

# Authentication endpoints
@app.post("/api/auth/register")
async def register_user(request: Request):
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        email = data.get("email", "")
        subscription_type = data.get("subscription_type", "free")
        
        if not username or not password:
            return JSONResponse(
                {"success": False, "message": "Username and password are required"},
                status_code=400
            )
        
        # For now, simulate successful registration
        return JSONResponse({
            "success": True,
            "message": "User registered successfully",
            "user": {
                "id": 1,
                "username": username,
                "email": email,
                "subscription_type": subscription_type,
                "expires_at": "2025-12-06T23:59:59",
                "note": "This is a demo response. Connect Supabase for real user management."
            }
        })
    except Exception as e:
        return JSONResponse(
            {"success": False, "message": f"Registration failed: {str(e)}"},
            status_code=500
        )

@app.post("/api/auth/login") 
async def login_user(request: Request):
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return JSONResponse(
                {"success": False, "message": "Username and password are required"},
                status_code=400
            )
        
        # Demo accounts
        demo_accounts = {
            "admin": "admin123",
            "demo": "demo123",
            "testuser": "testpass123"
        }
        
        if username in demo_accounts and demo_accounts[username] == password:
            return JSONResponse({
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": 1,
                    "username": username,
                    "subscription_type": "premium" if username == "admin" else "free",
                    "expires_at": "2025-12-31T23:59:59"
                },
                "token": "demo-jwt-token-" + username,
                "note": "This is a demo response. Connect Supabase for real authentication."
            })
        else:
            return JSONResponse(
                {"success": False, "message": "Invalid credentials"},
                status_code=401
            )
    except Exception as e:
        return JSONResponse(
            {"success": False, "message": f"Login failed: {str(e)}"},
            status_code=500
        )

@app.get("/api/auth/validate")
async def validate_token():
    return {
        "valid": True,
        "message": "Token validation endpoint",
        "note": "This is a demo response. Implement JWT validation for production."
    }

# Debug endpoint
@app.get("/debug")
async def debug_info():
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    
    return {
        "message": "Debug Information",
        "environment_variables": {
            "SUPABASE_URL": "✅ Set" if os.getenv("SUPABASE_URL") else "❌ Missing",
            "SUPABASE_ANON_KEY": "✅ Set" if os.getenv("SUPABASE_ANON_KEY") else "❌ Missing", 
            "JWT_SECRET": "✅ Set" if os.getenv("JWT_SECRET") else "❌ Missing",
            "ADMIN_USERNAME": "✅ Set" if os.getenv("ADMIN_USERNAME") else "❌ Missing",
            "ADMIN_PASSWORD": "✅ Set" if os.getenv("ADMIN_PASSWORD") else "❌ Missing",
        },
        "admin_credentials": {
            "username": admin_username,
            "password_length": len(admin_password),
            "password_starts_with": admin_password[:3] + "***" if admin_password else "Not set"
        },
        "demo_accounts": {
            "admin": "admin123",
            "demo": "demo123", 
            "testuser": "testpass123"
        },
        "endpoints": [
            "GET /",
            "GET /health", 
            "GET /admin",
            "POST /admin/login",
            "GET /docs",
            "POST /api/auth/register",
            "POST /api/auth/login",
            "GET /api/auth/validate",
            "GET /debug",
            "GET /test"
        ]
    }

# Subscription tier limits
SUBSCRIPTION_LIMITS = {
    "free": {"daily_limit": 10, "monthly_limit": 100, "total_limit": 1000},
    "premium": {"daily_limit": 100, "monthly_limit": 1000, "total_limit": 10000},
    "enterprise": {"daily_limit": 1000, "monthly_limit": 10000, "total_limit": 100000},
    "admin": {"daily_limit": -1, "monthly_limit": -1, "total_limit": -1}  # Unlimited
}

# Mock users database (in production, this would be in Supabase)
MOCK_USERS_DB = [
    {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "subscription_type": "admin",
        "expires_at": "2030-12-31T23:59:59",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00",
        "total_emails_sent": 0,
        "daily_emails_sent": 0,
        "monthly_emails_sent": 0,
        "last_email_date": None
    },
    {
        "id": 2,
        "username": "demo",
        "email": "demo@example.com", 
        "subscription_type": "free",
        "expires_at": "2025-12-31T23:59:59",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00",
        "total_emails_sent": 45,
        "daily_emails_sent": 3,
        "monthly_emails_sent": 45,
        "last_email_date": "2024-11-06"
    },
    {
        "id": 3,
        "username": "testuser",
        "email": "test@example.com",
        "subscription_type": "premium",
        "expires_at": "2025-06-15T23:59:59",
        "is_active": True,
        "created_at": "2024-02-15T00:00:00",
        "total_emails_sent": 123,
        "daily_emails_sent": 5,
        "monthly_emails_sent": 123,
        "last_email_date": "2024-11-06"
    }
]

# Admin user management endpoints
@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(request: Request, session: str = Cookie(None)):
    """Admin user management page"""
    # Check authentication
    if not verify_admin_session(session):
        return RedirectResponse(url="/admin/login", status_code=303)
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>User Management - Enhanced Email Sender</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; }}
            .card {{ background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }}
            .btn {{ background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; text-decoration: none; display: inline-block; }}
            .btn:hover {{ background: #5a6fd8; }}
            .btn-danger {{ background: #dc3545; }}
            .btn-danger:hover {{ background: #c82333; }}
            .btn-success {{ background: #28a745; }}
            .btn-success:hover {{ background: #218838; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f8f9fa; font-weight: bold; }}
            .status-active {{ color: #28a745; font-weight: bold; }}
            .status-expired {{ color: #dc3545; font-weight: bold; }}
            .form-group {{ margin-bottom: 15px; }}
            .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            .form-group input, .form-group select {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>👥 User Management</h1>
                <p>Manage user accounts, subscriptions, and monitor usage</p>
                <a href="/admin/dashboard" class="btn">← Back to Dashboard</a>
            </div>
            
            <!-- Add User Form -->
            <div class="card">
                <h3>➕ Add New User</h3>
                <form method="post" action="/admin/users/add">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                        <div class="form-group">
                            <label for="username">Username:</label>
                            <input type="text" name="username" required>
                        </div>
                        <div class="form-group">
                            <label for="password">Password:</label>
                            <input type="password" name="password" required>
                        </div>
                        <div class="form-group">
                            <label for="email">Email:</label>
                            <input type="email" name="email">
                        </div>
                        <div class="form-group">
                            <label for="subscription_type">Subscription:</label>
                            <select name="subscription_type">
                                <option value="free">Free</option>
                                <option value="premium">Premium</option>
                                <option value="enterprise">Enterprise</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-success">Add User</button>
                </form>
            </div>
            
            <!-- Users Table -->
            <div class="card">
                <h3>📋 All Users ({len(MOCK_USERS_DB)} total)</h3>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Subscription</th>
                            <th>Expires</th>
                            <th>Status</th>
                            <th>Emails Sent</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f'''
                        <tr>
                            <td>{user["id"]}</td>
                            <td><strong>{user["username"]}</strong></td>
                            <td>{user["email"]}</td>
                            <td><span class="{'badge-admin' if user["subscription_type"] == 'admin' else 'badge-premium' if user["subscription_type"] == 'premium' else 'badge-free'}">{user["subscription_type"].title()}</span></td>
                            <td>{user["expires_at"][:10]}</td>
                            <td><span class="{'status-active' if user["is_active"] else 'status-expired'}">{'Active' if user["is_active"] else 'Inactive'}</span></td>
                            <td>{user["total_emails_sent"]}</td>
                            <td>
                                <a href="/admin/users/{user["id"]}/extend" class="btn" style="font-size: 12px; padding: 5px 10px;">📅 Extend</a>
                                {'<a href="/admin/users/' + str(user["id"]) + '/delete" class="btn btn-danger" style="font-size: 12px; padding: 5px 10px;" onclick="return confirm(\'Delete this user?\')">🗑️ Delete</a>' if user["username"] != "admin" else ''}
                            </td>
                        </tr>
                        ''' for user in MOCK_USERS_DB])}
                    </tbody>
                </table>
            </div>
            
            <!-- Usage Statistics -->
            <div class="card">
                <h3>📊 Usage Statistics</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                    <div style="text-align: center; padding: 20px; background: #e3f2fd; border-radius: 8px;">
                        <h4>Total Users</h4>
                        <p style="font-size: 2em; margin: 0; color: #1976d2;">{len(MOCK_USERS_DB)}</p>
                    </div>
                    <div style="text-align: center; padding: 20px; background: #e8f5e8; border-radius: 8px;">
                        <h4>Active Users</h4>
                        <p style="font-size: 2em; margin: 0; color: #388e3c;">{len([u for u in MOCK_USERS_DB if u["is_active"]])}</p>
                    </div>
                    <div style="text-align: center; padding: 20px; background: #fff3e0; border-radius: 8px;">
                        <h4>Total Emails</h4>
                        <p style="font-size: 2em; margin: 0; color: #f57c00;">{sum(u["total_emails_sent"] for u in MOCK_USERS_DB)}</p>
                    </div>
                    <div style="text-align: center; padding: 20px; background: #fce4ec; border-radius: 8px;">
                        <h4>Premium Users</h4>
                        <p style="font-size: 2em; margin: 0; color: #c2185b;">{len([u for u in MOCK_USERS_DB if u["subscription_type"] in ["premium", "enterprise"]])}</p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

@app.post("/admin/users/add")
async def admin_add_user(request: Request):
    """Add new user"""
    try:
        form = await request.form()
        username = form.get("username", "").strip()
        password = form.get("password", "").strip()
        email = form.get("email", "").strip()
        subscription_type = form.get("subscription_type", "free")
        
        if not username or not password:
            return HTMLResponse("""
            <script>
                alert('Username and password are required!');
                window.history.back();
            </script>
            """)
        
        # Check if username exists
        if any(u["username"] == username for u in MOCK_USERS_DB):
            return HTMLResponse("""
            <script>
                alert('Username already exists!');
                window.history.back();
            </script>
            """)
        
        # Add new user
        new_user = {
            "id": max(u["id"] for u in MOCK_USERS_DB) + 1,
            "username": username,
            "email": email,
            "subscription_type": subscription_type,
            "expires_at": "2025-12-31T23:59:59" if subscription_type == "free" else "2026-12-31T23:59:59",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "total_emails_sent": 0
        }
        
        MOCK_USERS_DB.append(new_user)
        
        return HTMLResponse("""
        <script>
            alert('User added successfully!');
            window.location.href = '/admin/users';
        </script>
        """)
        
    except Exception as e:
        return HTMLResponse(f"""
        <script>
            alert('Error adding user: {str(e)}');
            window.history.back();
        </script>
        """)

@app.get("/admin/users/{user_id}/extend")
async def admin_extend_user(user_id: int):
    """Extend user subscription"""
    user = next((u for u in MOCK_USERS_DB if u["id"] == user_id), None)
    if user:
        # Extend by 30 days
        from datetime import datetime, timedelta
        current_expire = datetime.fromisoformat(user["expires_at"].replace('T', ' '))
        new_expire = current_expire + timedelta(days=30)
        user["expires_at"] = new_expire.isoformat()
        
        return HTMLResponse(f"""
        <script>
            alert('User subscription extended by 30 days!\\nNew expiration: {new_expire.strftime("%Y-%m-%d")}');
            window.location.href = '/admin/users';
        </script>
        """)
    else:
        return HTMLResponse("""
        <script>
            alert('User not found!');
            window.location.href = '/admin/users';
        </script>
        """)

@app.get("/admin/users/{user_id}/delete")
async def admin_delete_user(user_id: int):
    """Delete user"""
    global MOCK_USERS_DB
    user = next((u for u in MOCK_USERS_DB if u["id"] == user_id), None)
    
    if user:
        if user["username"] == "admin":
            return HTMLResponse("""
            <script>
                alert('Cannot delete admin user!');
                window.location.href = '/admin/users';
            </script>
            """)
        
        MOCK_USERS_DB = [u for u in MOCK_USERS_DB if u["id"] != user_id]
        
        return HTMLResponse(f"""
        <script>
            alert('User "{user["username"]}" deleted successfully!');
            window.location.href = '/admin/users';
        </script>
        """)
    else:
        return HTMLResponse("""
        <script>
            alert('User not found!');
            window.location.href = '/admin/users';
        </script>
        """)

# Add compatibility endpoints for desktop app
@app.post("/login")
async def login_compat(request: Request):
    """Compatibility endpoint for desktop app login"""
    form = await request.form()
    username = form.get("username", "").strip()
    password = form.get("password", "").strip()
    
    # Check demo accounts
    if username == "admin" and password == "admin123":
        user_data = {"username": "admin", "role": "admin", "id": 1}
    elif username == "demo" and password == "demo123":
        user_data = {"username": "demo", "role": "user", "id": 2}
    elif username == "testuser" and password == "testpass123":
        user_data = {"username": "testuser", "role": "user", "id": 3}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT token
    token_data = {"sub": username, "role": user_data["role"]}
    if jwt:
        access_token = jwt.encode(token_data, JWT_SECRET, algorithm="HS256")
    else:
        # Fallback token for demo purposes
        access_token = f"demo_token_{username}_{user_data['role']}"
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request, session: str = Cookie(None)):
    """Admin dashboard page with navigation to user management"""
    # Check authentication
    if not verify_admin_session(session):
        return RedirectResponse(url="/admin/login", status_code=303)
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard - Enhanced Email Sender</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem; }}
            .card {{ background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }}
            .btn {{ background: #667eea; color: white; padding: 15px 25px; border: none; border-radius: 5px; cursor: pointer; margin: 10px; text-decoration: none; display: inline-block; font-size: 16px; }}
            .btn:hover {{ background: #5a6fd8; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }}
            .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Admin Dashboard</h1>
                <p>Enhanced Email Sender - Cloud Management System</p>
            </div>
            
            <div class="card">
                <h3>Admin Controls</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                    <a href="/admin/users" class="btn">Manage Users</a>
                    <a href="/debug" class="btn">System Debug</a>
                    <a href="/health" class="btn">Health Status</a>
                    <a href="/docs" class="btn">API Documentation</a>
                </div>
            </div>
            
            <div class="card">
                <h3>System Overview</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{len(MOCK_USERS_DB)}</div>
                        <div>Total Users</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len([u for u in MOCK_USERS_DB if u["is_active"]])}</div>
                        <div>Active Users</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{sum(u["total_emails_sent"] for u in MOCK_USERS_DB)}</div>
                        <div>Total Emails Sent</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len([u for u in MOCK_USERS_DB if u["subscription_type"] in ["premium", "enterprise"]])}</div>
                        <div>Premium Users</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>Quick Actions</h3>
                <p>
                    <strong>Desktop App Integration:</strong> Users can download and run the desktop app, 
                    which will connect to this cloud system for authentication and data storage.
                </p>
                <p>
                    <strong>User Management:</strong> Add, remove, and manage user subscriptions through the user management interface.
                </p>
                <p>
                    <strong>Real-time Monitoring:</strong> Track user activity and system health through the debug and health endpoints.
                </p>
            </div>
        </div>
    </body>
    </html>
    """)

# Email statistics tracking
@app.post("/api/stats/update")
async def update_email_stats(request: Request):
    """Update user email sending statistics"""
    try:
        data = await request.json()
        emails_sent = data.get("emails_sent", 0)
        username = data.get("username", "demo")  # In production, get from JWT
        campaign_name = data.get("campaign_name", f"Campaign {datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Find and update user
        user = next((u for u in MOCK_USERS_DB if u["username"] == username), None)
        if user:
            user["total_emails_sent"] += emails_sent
            user["daily_emails_sent"] += emails_sent
            user["monthly_emails_sent"] += emails_sent
            user["last_email_date"] = datetime.now().strftime("%Y-%m-%d")
            
            # Log campaign (in production, this would be in database)
            campaign_log = {
                "campaign_name": campaign_name,
                "emails_sent": emails_sent,
                "timestamp": datetime.now().isoformat(),
                "username": username
            }
            
            return {
                "success": True,
                "message": f"Updated stats: {emails_sent} emails sent",
                "total_emails": user["total_emails_sent"],
                "campaign": campaign_log
            }
        else:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "User not found"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/api/user/info")
async def get_user_info(request: Request):
    """Get user information and subscription status"""
    try:
        # In production, this would verify JWT token and get from database
        # For demo, return demo user data with subscription limits
        user = MOCK_USERS_DB[1]  # Demo user
        limits = SUBSCRIPTION_LIMITS[user["subscription_type"]]
        
        # Calculate remaining emails
        daily_remaining = limits["daily_limit"] - user["daily_emails_sent"] if limits["daily_limit"] != -1 else -1
        monthly_remaining = limits["monthly_limit"] - user["monthly_emails_sent"] if limits["monthly_limit"] != -1 else -1
        total_remaining = limits["total_limit"] - user["total_emails_sent"] if limits["total_limit"] != -1 else -1
        
        return {
            "success": True,
            "user": {
                "username": user["username"],
                "email": user["email"],
                "subscription_type": user["subscription_type"],
                "expires_at": user["expires_at"],
                "is_active": user["is_active"],
                "total_emails_sent": user["total_emails_sent"],
                "daily_emails_sent": user["daily_emails_sent"],
                "monthly_emails_sent": user["monthly_emails_sent"],
                "limits": limits,
                "remaining": {
                    "daily": daily_remaining,
                    "monthly": monthly_remaining,
                    "total": total_remaining
                }
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/validate/subscription")
async def validate_subscription(request: Request):
    """Validate if user can send emails based on subscription"""
    try:
        data = await request.json()
        email_count = data.get("email_count", 1)
        username = data.get("username", "demo")  # In production, get from JWT
        
        # Find user
        user = next((u for u in MOCK_USERS_DB if u["username"] == username), None)
        if not user:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "User not found"}
            )
        
        # Check if subscription is active
        if not user["is_active"]:
            return {
                "success": False,
                "error": "Account is inactive",
                "can_send": False
            }
        
        # Check expiration
        expire_date = datetime.fromisoformat(user["expires_at"])
        if expire_date < datetime.now():
            return {
                "success": False,
                "error": "Subscription expired",
                "can_send": False,
                "expires_at": user["expires_at"]
            }
        
        # Check limits
        limits = SUBSCRIPTION_LIMITS[user["subscription_type"]]
        
        # Check daily limit
        if limits["daily_limit"] != -1:
            if user["daily_emails_sent"] + email_count > limits["daily_limit"]:
                return {
                    "success": False,
                    "error": f"Daily limit exceeded. Limit: {limits['daily_limit']}, Used: {user['daily_emails_sent']}",
                    "can_send": False,
                    "limits": limits
                }
        
        # Check monthly limit
        if limits["monthly_limit"] != -1:
            if user["monthly_emails_sent"] + email_count > limits["monthly_limit"]:
                return {
                    "success": False,
                    "error": f"Monthly limit exceeded. Limit: {limits['monthly_limit']}, Used: {user['monthly_emails_sent']}",
                    "can_send": False,
                    "limits": limits
                }
        
        # Check total limit
        if limits["total_limit"] != -1:
            if user["total_emails_sent"] + email_count > limits["total_limit"]:
                return {
                    "success": False,
                    "error": f"Total limit exceeded. Limit: {limits['total_limit']}, Used: {user['total_emails_sent']}",
                    "can_send": False,
                    "limits": limits
                }
        
        # Calculate days until expiration
        days_until_expiry = (expire_date - datetime.now()).days
        
        return {
            "success": True,
            "can_send": True,
            "message": "Validation successful",
            "limits": limits,
            "usage": {
                "daily": user["daily_emails_sent"],
                "monthly": user["monthly_emails_sent"],
                "total": user["total_emails_sent"]
            },
            "days_until_expiry": days_until_expiry,
            "warnings": [] if days_until_expiry > 7 else [f"Subscription expires in {days_until_expiry} days"]
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

# Campaign history tracking
@app.get("/api/campaigns/history")
async def get_campaign_history(request: Request):
    """Get email campaign history for user"""
    try:
        username = request.query_params.get("username", "demo") # In production, get from JWT
        
        # Mock campaign history (in production, query from database)
        campaigns = [
            {
                "id": 1,
                "campaign_name": "Welcome Series",
                "emails_sent": 25,
                "timestamp": "2024-11-01T10:00:00",
                "status": "completed",
                "success_rate": 96.0
            },
            {
                "id": 2,
                "campaign_name": "Product Update",
                "emails_sent": 15,
                "timestamp": "2024-11-03T14:30:00",
                "status": "completed",
                "success_rate": 100.0
            },
            {
                "id": 3,
                "campaign_name": "Newsletter Nov",
                "emails_sent": 5,
                "timestamp": "2024-11-06T09:15:00",
                "status": "completed",
                "success_rate": 100.0
            }
        ]
        
        return {
            "success": True,
            "campaigns": campaigns,
            "total_campaigns": len(campaigns),
            "total_emails_sent": sum(c["emails_sent"] for c in campaigns)
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/admin/analytics")
async def admin_analytics(request: Request):
    """Get analytics data for admin dashboard"""
    try:
        # Calculate analytics from user data
        total_users = len(MOCK_USERS_DB)
        active_users = len([u for u in MOCK_USERS_DB if u["is_active"]])
        total_emails = sum(u["total_emails_sent"] for u in MOCK_USERS_DB)
        
        # Subscription breakdown
        subscription_breakdown = {}
        for user in MOCK_USERS_DB:
            sub_type = user["subscription_type"]
            if sub_type not in subscription_breakdown:
                subscription_breakdown[sub_type] = {"count": 0, "emails_sent": 0}
            subscription_breakdown[sub_type]["count"] += 1
            subscription_breakdown[sub_type]["emails_sent"] += user["total_emails_sent"]
        
        # Recent activity (mock data)
        recent_activity = [
            {"username": "demo", "action": "sent_emails", "count": 5, "timestamp": "2024-11-06T09:15:00"},
            {"username": "testuser", "action": "sent_emails", "count": 3, "timestamp": "2024-11-06T08:30:00"},
            {"username": "demo", "action": "login", "timestamp": "2024-11-06T08:00:00"}
        ]
        
        return {
            "success": True,
            "analytics": {
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "inactive": total_users - active_users
                },
                "emails": {
                    "total_sent": total_emails,
                    "today": sum(u["daily_emails_sent"] for u in MOCK_USERS_DB),
                    "this_month": sum(u["monthly_emails_sent"] for u in MOCK_USERS_DB)
                },
                "subscriptions": subscription_breakdown,
                "recent_activity": recent_activity
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

# Test endpoint
@app.get("/test")
async def test():
    return {
        "message": "Test endpoint working perfectly!",
        "status": "success",
        "environment": "production" if os.getenv("VERCEL") else "development"
    }