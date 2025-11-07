#!/usr/bin/env python3
"""
Enhanced Email Sender - Production API
Handles missing dependencies gracefully for Vercel deployment
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exception_handlers import http_exception_handler
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import jwt
import json
from datetime import datetime, timedelta
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Enhanced Email Sender API", version="1.0.0")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc),
            "path": str(request.url)
        }
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="admin/static"), name="static")

@app.get("/")
async def root():
    """Redirect root to download page"""
    return RedirectResponse(url="/download")

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page"""
    if templates is None:
        raise HTTPException(status_code=500, detail="Templates not loaded")
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin/login")
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle admin login"""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/admin/dashboard", status_code=302)
        token = create_jwt_token({"username": username, "role": "admin"})
        response.set_cookie(key="admin_token", value=token, httponly=True)
        return response
    
    return templates.TemplateResponse(
        "admin_login.html",
        {"request": request, "error": "Invalid credentials"},
        status_code=401
    )

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard page"""
    token = request.cookies.get("admin_token")
    if not token:
        return RedirectResponse(url="/admin/login")
    
    try:
        payload = verify_jwt_token(token)
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not an admin")
        
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "username": payload.get("username")
        })
    except:
        response = RedirectResponse(url="/admin/login")
        response.delete_cookie("admin_token")
        return response

# Templates and static files
templates = None
try:
    templates = Jinja2Templates(directory="admin/templates")
    logger.info("Templates loaded successfully")
except Exception as e:
    logger.warning(f"Could not load templates: {e}")

# Don't mount static files here - let Vercel handle them via routing

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Security
security = HTTPBearer()

# Pydantic models
class UserRegistration(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    subscription_type: str = "free"

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    subscription_type: str
    expires_at: str
    is_active: bool

# Utility functions
def create_jwt_token(user_data: Dict) -> str:
    """Create JWT token for user"""
    payload = {
        "user_id": user_data.get("id"),
        "username": user_data.get("username"),
        "subscription_type": user_data.get("subscription_type"),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt_token(token: str) -> Dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    try:
        import bcrypt
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    except ImportError:
        # Fallback for development (not secure for production)
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password"""
    try:
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except ImportError:
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest() == hashed

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_jwt_token(token)
    return payload

# Mock database for testing when Supabase isn't available
MOCK_USERS = [
    {
        "id": 1,
        "username": "admin",
        "hashed_password": hash_password("admin123"),
        "email": "admin@example.com",
        "subscription_type": "admin",
        "expires_at": "2030-12-31T23:59:59",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00"
    },
    {
        "id": 2,
        "username": "demo",
        "hashed_password": hash_password("demo123"),
        "email": "demo@example.com",
        "subscription_type": "free",
        "expires_at": "2025-12-31T23:59:59",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00"
    }
]

class DatabaseService:
    """Database service with fallback to mock data"""
    
    def __init__(self):
        self.use_supabase = bool(SUPABASE_URL and SUPABASE_ANON_KEY)
        if self.use_supabase:
            try:
                import httpx
                self.httpx_available = True
            except ImportError:
                self.httpx_available = False
                self.use_supabase = False
        
        if not self.use_supabase:
            logger.warning("Using mock database - not suitable for production")
    
    async def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        if self.use_supabase and self.httpx_available:
            try:
                import httpx
                headers = {
                    "apikey": SUPABASE_ANON_KEY,
                    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                    "Content-Type": "application/json"
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{SUPABASE_URL}/rest/v1/users",
                        headers=headers,
                        params={"username": f"eq.{username}", "select": "*"}
                    )
                    
                    if response.status_code == 200:
                        users = response.json()
                        return users[0] if users else None
            except Exception as e:
                logger.error(f"Supabase error: {e}")
        
        # Fallback to mock data
        for user in MOCK_USERS:
            if user["username"] == username:
                return user
        return None
    
    async def create_user(self, user_data: Dict) -> Dict:
        """Create new user"""
        if self.use_supabase and self.httpx_available:
            try:
                import httpx
                headers = {
                    "apikey": SUPABASE_SERVICE_KEY or SUPABASE_ANON_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY or SUPABASE_ANON_KEY}",
                    "Content-Type": "application/json"
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SUPABASE_URL}/rest/v1/users",
                        headers=headers,
                        json=user_data
                    )
                    
                    if response.status_code in [200, 201]:
                        return response.json()[0]
            except Exception as e:
                logger.error(f"Supabase error: {e}")
        
        # Fallback to mock data
        new_user = {
            "id": len(MOCK_USERS) + 1,
            **user_data,
            "created_at": datetime.utcnow().isoformat()
        }
        MOCK_USERS.append(new_user)
        return new_user

# Initialize database service
db = DatabaseService()

# API Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Enhanced Email Sender API",
        "status": "active",
        "version": "1.0.0",
        "database": "supabase" if db.use_supabase else "mock"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database_connected": db.use_supabase,
        "templates_loaded": templates is not None,
        "environment_variables": {
            "SUPABASE_URL": "✅" if SUPABASE_URL else "❌",
            "SUPABASE_ANON_KEY": "✅" if SUPABASE_ANON_KEY else "❌",
            "JWT_SECRET": "✅" if JWT_SECRET else "❌",
            "ADMIN_USERNAME": "✅" if ADMIN_USERNAME else "❌",
            "ADMIN_PASSWORD": "✅" if ADMIN_PASSWORD else "❌"
        }
    }

@app.get("/debug")
async def debug_info():
    """Debug endpoint"""
    return {
        "message": "Debug Information",
        "environment_variables": {
            "SUPABASE_URL": "✅ Set" if SUPABASE_URL else "❌ Missing",
            "SUPABASE_ANON_KEY": "✅ Set" if SUPABASE_ANON_KEY else "❌ Missing",
            "JWT_SECRET": "✅ Set" if JWT_SECRET else "❌ Missing",
            "ADMIN_USERNAME": "✅ Set" if ADMIN_USERNAME else "❌ Missing",
            "ADMIN_PASSWORD": "✅ Set" if ADMIN_PASSWORD else "❌ Missing",
        },
        "database_status": "Supabase" if db.use_supabase else "Mock",
        "templates_status": "Loaded" if templates else "Not loaded",
        "total_mock_users": len(MOCK_USERS)
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {
        "message": "Test endpoint working",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/auth/register")
async def register_user(user: UserRegistration):
    """Register new user"""
    try:
        # Check if user exists
        existing_user = await db.get_user_by_username(user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Create user
        expires_at = datetime.utcnow() + timedelta(days=30)  # 30 days free trial
        user_data = {
            "username": user.username,
            "hashed_password": hash_password(user.password),
            "email": user.email,
            "subscription_type": user.subscription_type,
            "expires_at": expires_at.isoformat(),
            "is_active": True
        }
        
        new_user = await db.create_user(user_data)
        token = create_jwt_token(new_user)
        
        return {
            "message": "User registered successfully",
            "token": token,
            "user": {
                "id": new_user["id"],
                "username": new_user["username"],
                "subscription_type": new_user["subscription_type"],
                "expires_at": new_user["expires_at"]
            }
        }
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
async def login_user(user: UserLogin):
    """Login user"""
    try:
        # Get user from database
        db_user = await db.get_user_by_username(user.username)
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password
        if not verify_password(user.password, db_user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if user is active
        if not db_user["is_active"]:
            raise HTTPException(status_code=401, detail="Account is inactive")
        
        # Create token
        token = create_jwt_token(db_user)
        
        return {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": db_user["id"],
                "username": db_user["username"],
                "subscription_type": db_user["subscription_type"],
                "expires_at": db_user["expires_at"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/api/auth/validate")
async def validate_token(current_user: Dict = Depends(get_current_user)):
    """Validate JWT token"""
    return {
        "valid": True,
        "user": current_user
    }

# Admin routes
@app.get("/admin", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page"""
    try:
        if templates:
            return templates.TemplateResponse("admin_login.html", {"request": request})
    except Exception as e:
        logger.warning(f"Template error: {e}")
    
    # Fallback HTML
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enhanced Email Sender - Admin Login</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 400px; margin: 100px auto; padding: 20px; }
            .login-form { background: #f5f5f5; padding: 30px; border-radius: 10px; }
            input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #007bff; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="login-form">
            <h2>Admin Login</h2>
            <form method="post" action="/admin/login">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
        </div>
    </body>
    </html>
    """)

@app.post("/admin/login")
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Admin login"""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Check if request accepts JSON (API call) or HTML (form submission)
        accept_header = request.headers.get("accept", "")
        if "application/json" in accept_header:
            return JSONResponse({
                "success": True,
                "message": "Admin login successful",
                "redirect": "/admin/dashboard"
            })
        else:
            return RedirectResponse(url="/admin/dashboard", status_code=302)
    else:
        if "application/json" in request.headers.get("accept", ""):
            return JSONResponse({
                "success": False,
                "message": "Invalid admin credentials"
            }, status_code=401)
        else:
            raise HTTPException(status_code=401, detail="Invalid admin credentials")

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard"""
    if not templates:
        return HTMLResponse("""
        <html><body>
        <h1>Admin Dashboard</h1>
        <p>Total Users: {}</p>
        <p>Database: {}</p>
        <p>Status: Online</p>
        </body></html>
        """.format(len(MOCK_USERS), "Supabase" if db.use_supabase else "Mock"))
    
    # Get user stats
    stats = {
        "total_users": len(MOCK_USERS),
        "database_type": "Supabase" if db.use_supabase else "Mock"
    }
    
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "stats": stats,
        "users": MOCK_USERS
    })

# For Vercel deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)