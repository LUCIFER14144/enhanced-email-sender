from fastapi import FastAPI, HTTPException, Request, Form, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import jwt
import bcrypt
import os
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict
from pydantic import BaseModel

app = FastAPI()

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    subscription_tier: str = "free"
    daily_email_limit: int = 100

# Supabase client
class SupabaseClient:
    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_SERVICE_KEY
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
    
    async def select(self, table: str, columns: str = "*", filters: Dict = None):
        url = f"{self.url}/rest/v1/{table}"
        params = {"select": columns}
        
        if filters:
            for key, value in filters.items():
                params[f"{key}"] = f"eq.{value}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return []
                else:
                    logger.error(f"Database error: {response.status_code} - {response.text}")
                    raise HTTPException(status_code=500, detail="Database error occurred")
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise HTTPException(status_code=500, detail="Could not connect to database")
    
    async def insert(self, table: str, data: Dict):
        url = f"{self.url}/rest/v1/{table}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            if response.status_code in [200, 201]:
                return response.json()
            raise HTTPException(status_code=400, detail="Insert failed")
    
    async def update(self, table: str, data: Dict, filters: Dict):
        url = f"{self.url}/rest/v1/{table}"
        params = {}
        
        for key, value in filters.items():
            params[f"{key}"] = f"eq.{value}"
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=self.headers, params=params, json=data)
            if response.status_code == 200:
                return response.json()
            raise HTTPException(status_code=400, detail="Update failed")
    
    async def delete(self, table: str, filters: Dict):
        url = f"{self.url}/rest/v1/{table}"
        params = {}
        
        for key, value in filters.items():
            params[f"{key}"] = f"eq.{value}"
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return True
            raise HTTPException(status_code=400, detail="Delete failed")

supabase = SupabaseClient()

# Verify admin session
async def verify_admin_session(request: Request):
    token = request.cookies.get("admin_token")
    if not token:
        raise HTTPException(status_code=401, detail="Admin authentication required")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        return True
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid admin token")

# Routes
@app.get("/admin")
async def admin_root(request: Request):
    token = request.cookies.get("admin_token")
    if token:
        try:
            jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return RedirectResponse(url="/admin/dashboard")
        except:
            pass
    return RedirectResponse(url="/admin/login")

@app.get("/admin/login")
async def admin_login_page():
    with open("admin/templates/new_admin_login.html") as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.post("/admin/login")
async def admin_login(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        token = jwt.encode(
            {
                "sub": username,
                "role": "admin",
                "exp": datetime.utcnow() + timedelta(hours=24)
            },
            JWT_SECRET,
            algorithm="HS256"
        )
        response = RedirectResponse(url="/admin/dashboard", status_code=303)
        response.set_cookie(key="admin_token", value=token, httponly=True)
        return response
    
    return RedirectResponse(url="/admin/login?error=1", status_code=303)

@app.get("/admin/dashboard")
async def admin_dashboard(request: Request, _=Depends(verify_admin_session)):
    with open("admin/templates/new_admin_dashboard.html") as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.get("/admin/logout")
async def admin_logout():
    response = RedirectResponse(url="/admin/login")
    response.delete_cookie("admin_token")
    return response

# Models
class UserBase(BaseModel):
    username: str
    email: str
    subscription_tier: str = "free"
    daily_email_limit: int = 100
    is_active: bool = True
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class TemplateCreate(BaseModel):
    template_name: str
    subject: str
    body_text: str
    body_html: str

class SystemSettings(BaseModel):
    default_daily_limit: int = 100
    max_file_size: int = 10
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    system_email: Optional[str] = None
    free_tier_templates: bool = False
    free_tier_scheduling: bool = False
    free_tier_api: bool = False

# API Routes - Users
@app.get("/api/admin/users")
async def list_users(_=Depends(verify_admin_session)):
    users = await supabase.select("users", "*")
    for user in users:
        stats = await supabase.select("usage_stats", "*", {"user_id": user["id"]})
        user["usage_stats"] = stats
    return users or []

@app.post("/api/admin/users")
async def create_user(user: UserCreate, _=Depends(verify_admin_session)):
    # Check if username exists
    existing = await supabase.select("users", "*", {"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash password
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    
    # Create user data
    user_data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed,
        "subscription_tier": user.subscription_tier,
        "subscription_start": datetime.utcnow().isoformat(),
        "subscription_end": (datetime.utcnow() + timedelta(days=365)).isoformat(),
        "daily_email_limit": user.daily_email_limit,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Insert user
    result = await supabase.insert("users", user_data)
    return {"message": "User created successfully", "user": result[0]}

@app.put("/api/admin/users/{user_id}")
async def update_user(user_id: int, user: UserUpdate, _=Depends(verify_admin_session)):
    # Update user data
    update_data = user.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = bcrypt.hashpw(update_data.pop("password").encode(), bcrypt.gensalt()).decode()
    
    update_data["updated_at"] = datetime.utcnow().isoformat()
    result = await supabase.update("users", update_data, {"id": user_id})
    return {"message": "User updated successfully", "user": result[0]}

@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: int, _=Depends(verify_admin_session)):
    await supabase.delete("users", {"id": user_id})
    return {"message": "User deleted successfully"}

# API Routes - Email Templates
@app.get("/api/admin/templates")
async def list_templates(_=Depends(verify_admin_session)):
    templates = await supabase.select("email_templates", "*")
    return templates or []

@app.post("/api/admin/templates")
async def create_template(template: TemplateCreate, _=Depends(verify_admin_session)):
    template_data = template.dict()
    template_data["created_at"] = datetime.utcnow().isoformat()
    result = await supabase.insert("email_templates", template_data)
    return {"message": "Template created successfully", "template": result[0]}

# API Routes - System Settings
@app.get("/api/admin/settings")
async def get_settings(_=Depends(verify_admin_session)):
    settings = await supabase.select("system_settings", "*")
    return settings[0] if settings else {}

@app.put("/api/admin/settings")
async def update_settings(settings: SystemSettings, _=Depends(verify_admin_session)):
    settings_data = settings.dict()
    settings_data["updated_at"] = datetime.utcnow().isoformat()
    
    current_settings = await supabase.select("system_settings", "*")
    if current_settings:
        result = await supabase.update("system_settings", settings_data, {"id": current_settings[0]["id"]})
    else:
        result = await supabase.insert("system_settings", settings_data)
    
    return {"message": "Settings updated successfully", "settings": result[0]}

# API Routes - Usage Stats
@app.get("/api/admin/stats")
async def get_stats(_=Depends(verify_admin_session)):
    stats = {
        "total_users": len(await supabase.select("users", "*")),
        "active_users": len(await supabase.select("users", "*", {"is_active": True})),
        "total_emails": sum(user.get("total_emails_sent", 0) for user in await supabase.select("users", "*")),
        "templates": len(await supabase.select("email_templates", "*")),
        "campaigns": len(await supabase.select("email_campaigns", "*"))
    }
    return stats