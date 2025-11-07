from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import jwt
import bcrypt
import json
from datetime import datetime, timedelta
import logging
import asyncio
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Enhanced Email Sender API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates and static files
templates = Jinja2Templates(directory="admin/templates")
app.mount("/static", StaticFiles(directory="admin/static"), name="static")

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Security
security = HTTPBearer()

# Supabase client setup
class Campaign(BaseModel):
    name: str
    template_type: str
    subject: str
    content: str
    recipients: str

class SupabaseClient:
    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_SERVICE_KEY or SUPABASE_ANON_KEY
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
    
    async def select(self, table: str, columns: str = "*", filters: Dict = None):
        """Select data from Supabase table"""
        url = f"{self.url}/rest/v1/{table}"
        params = {"select": columns}
        
        if filters:
            for key, value in filters.items():
                params[f"{key}"] = f"eq.{value}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            return []
    
    async def insert(self, table: str, data: Dict):
        """Insert data into Supabase table"""
        url = f"{self.url}/rest/v1/{table}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=data)
            if response.status_code in [200, 201]:
                return response.json()
            raise HTTPException(status_code=400, detail="Insert failed")
    
    async def update(self, table: str, data: Dict, filters: Dict):
        """Update data in Supabase table"""
        url = f"{self.url}/rest/v1/{table}"
        params = {}
        
        for key, value in filters.items():
            params[f"{key}"] = f"eq.{value}"
        
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=self.headers, params=params, json=data)
            if response.status_code in [200, 201]:
                return response.json()
            raise HTTPException(status_code=400, detail="Update failed")

    async def create_campaign(self, campaign_data: Dict):
        """Create a new campaign in Supabase"""
        return await self.insert("campaigns", campaign_data)
            if response.status_code == 200:
                return response.json()
            raise HTTPException(status_code=400, detail="Update failed")
    
    async def delete(self, table: str, filters: Dict):
        """Delete data from Supabase table"""
        url = f"{self.url}/rest/v1/{table}"
        params = {}
        
        for key, value in filters.items():
            params[f"{key}"] = f"eq.{value}"
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.headers, params=params)
            return response.status_code == 200

supabase = SupabaseClient()

# Pydantic models
class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = ""
    subscription_type: str = "free"
    expires_at: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class RecipientList(BaseModel):
    list_name: str
    recipients: List[str]

class ExtendSubscription(BaseModel):
    days: int

class SetExpiration(BaseModel):
    expiration_date: str
    subscription_type: str = "premium"

class AdminUserCreate(BaseModel):
    username: str
    email: str
    password: str
    subscription_tier: str = "free"
    daily_email_limit: int = 100
    subscription_end: str

class SystemSettings(BaseModel):
    default_daily_limit: int = 100
    max_file_size: int = 10
    smtp_host: str
    smtp_port: int = 587
    system_email: str
    free_tier_templates: bool = False
    free_tier_scheduling: bool = False
    free_tier_api: bool = False

# Helper functions
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_admin_session(request: Request):
    """Verify admin session"""
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

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())

def calculate_days_remaining(expires_at: str) -> int:
    """Calculate days remaining until expiration"""
    try:
        expiry_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        days = (expiry_date.replace(tzinfo=None) - datetime.utcnow()).days
        return max(0, days)
    except:
        return 0

# Admin User Management

@app.post("/api/admin/users")
async def create_admin_user(user: AdminUserCreate, request: Request):
    """Create a new user (admin only)"""
    # Verify admin session
    await verify_admin_session(request)
    
    try:
        # Hash the password
        hashed_password = hash_password(user.password)
        
        # Create user data
        user_data = {
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
            "subscription_tier": user.subscription_tier,
            "subscription_start": datetime.utcnow().isoformat(),
            "subscription_end": user.subscription_end,
            "daily_email_limit": user.daily_email_limit,
            "is_active": True
        }
        
        # Check if username already exists
        existing_user = await supabase.select("users", "*", {"username": user.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Create user in database
        result = await supabase.insert("users", user_data)
        
        # Log user creation
        await supabase.insert("usage_logs", {
            "user_id": result[0]["id"],
            "action": "user_created",
            "details": f"User created by admin with subscription tier: {user.subscription_tier}"
        })
        
        return {"message": "User created successfully", "user_id": result[0]["id"]}
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

# Admin Settings Management

@app.get("/api/admin/settings")
async def get_system_settings(request: Request):
    """Get system settings"""
    # Verify admin session
    await verify_admin_session(request)
    
    try:
        # Get settings from database
        settings = await supabase.select("system_settings", "*")
        if not settings:
            # Return default settings if none exist
            return {
                "default_daily_limit": 100,
                "max_file_size": 10,
                "smtp_host": "",
                "smtp_port": 587,
                "system_email": "",
                "free_tier_templates": False,
                "free_tier_scheduling": False,
                "free_tier_api": False
            }
        return settings[0]
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting settings: {str(e)}")

@app.post("/api/admin/settings")
async def update_system_settings(settings: SystemSettings, request: Request):
    """Update system settings"""
    # Verify admin session
    await verify_admin_session(request)
    
    try:
        # Check if settings exist
        existing_settings = await supabase.select("system_settings", "*")
        
        settings_data = {
            "default_daily_limit": settings.default_daily_limit,
            "max_file_size": settings.max_file_size,
            "smtp_host": settings.smtp_host,
            "smtp_port": settings.smtp_port,
            "system_email": settings.system_email,
            "free_tier_templates": settings.free_tier_templates,
            "free_tier_scheduling": settings.free_tier_scheduling,
            "free_tier_api": settings.free_tier_api,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if existing_settings:
            # Update existing settings
            await supabase.update("system_settings", settings_data, {"id": existing_settings[0]["id"]})
        else:
            # Create new settings
            await supabase.insert("system_settings", settings_data)
        
        return {"message": "Settings updated successfully"}
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating settings: {str(e)}")

# Admin Campaign Management

@app.post("/api/admin/campaigns")
async def create_campaign(campaign: Campaign, request: Request):
    """Create a new email campaign"""
    # Verify admin session
    await verify_admin_session(request)
    
    try:
        # Get Supabase client
        supabase = SupabaseClient()
        
        # Create campaign record
        campaign_data = {
            "name": campaign.name,
            "template_type": campaign.template_type,
            "subject": campaign.subject,
            "content": campaign.content,
            "recipients": campaign.recipients,
            "status": "draft",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Insert campaign into database
        result = await supabase.create_campaign(campaign_data)
        
        return {"message": "Campaign created successfully", "campaign_id": result.get("id")}
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating campaign: {str(e)}")

# API Routes

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "Enhanced Email Sender API",
        "status": "active",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Authentication endpoints
@app.post("/api/auth/register")
async def register_user(user: UserRegister):
    """Register a new user"""
    try:
        # Check if user exists
        existing_users = await supabase.select("users", filters={"username": user.username})
        if existing_users:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Set default expiration if not provided
        if not user.expires_at:
            expiry_date = datetime.utcnow() + timedelta(days=30)
            user.expires_at = expiry_date.isoformat()
        
        # Create user data
        user_data = {
            "username": user.username,
            "hashed_password": hash_password(user.password),
            "email": user.email,
            "subscription_type": user.subscription_type,
            "expires_at": user.expires_at,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "total_emails_sent": 0
        }
        
        await supabase.insert("users", user_data)
        
        return {"success": True, "message": "User registered successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/auth/login")
async def login_user(user: UserLogin):
    """Login user and return JWT token"""
    try:
        # Get user from database
        users = await supabase.select("users", filters={"username": user.username})
        if not users:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_data = users[0]
        
        # Verify password
        if not verify_password(user.password, user_data["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if account is active
        if not user_data.get("is_active", True):
            raise HTTPException(status_code=401, detail="Account deactivated")
        
        # Check expiration
        days_remaining = calculate_days_remaining(user_data["expires_at"])
        if days_remaining <= 0:
            raise HTTPException(status_code=401, detail="Subscription expired")
        
        # Update last login
        await supabase.update("users", 
                            {"last_login": datetime.utcnow().isoformat()}, 
                            {"id": user_data["id"]})
        
        # Generate JWT token
        token_payload = {
            "user_id": user_data["id"],
            "username": user.username,
            "subscription_type": user_data.get("subscription_type", "free"),
            "expires_at": user_data["expires_at"],
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(token_payload, JWT_SECRET, algorithm="HS256")
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user_data["id"],
                "username": user.username,
                "email": user_data.get("email", ""),
                "subscription_type": user_data.get("subscription_type", "free"),
                "expires_at": user_data["expires_at"],
                "days_remaining": days_remaining,
                "total_emails_sent": user_data.get("total_emails_sent", 0)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/api/auth/status")
async def get_auth_status(user_id: int = Depends(verify_token)):
    """Get current user status and subscription info"""
    try:
        users = await supabase.select("users", filters={"id": user_id})
        if not users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = users[0]
        days_remaining = calculate_days_remaining(user["expires_at"])
        
        if days_remaining <= 0:
            raise HTTPException(status_code=401, detail="Subscription expired")
        
        return {
            "success": True,
            "user_id": user_id,
            "username": user["username"],
            "subscription_type": user.get("subscription_type", "free"),
            "days_remaining": days_remaining,
            "expires_at": user["expires_at"],
            "is_active": user.get("is_active", True),
            "total_emails_sent": user.get("total_emails_sent", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")

# Recipient management endpoints
@app.post("/api/recipients/save")
async def save_recipients(recipients: RecipientList, user_id: int = Depends(verify_token)):
    """Save recipient list to cloud"""
    try:
        # Check if list exists
        existing = await supabase.select("recipient_lists", 
                                       filters={"user_id": user_id, "list_name": recipients.list_name})
        
        recipient_data = {
            "user_id": user_id,
            "list_name": recipients.list_name,
            "recipients": json.dumps(recipients.recipients),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if existing:
            # Update existing list
            await supabase.update("recipient_lists", recipient_data, {"id": existing[0]["id"]})
        else:
            # Create new list
            recipient_data["created_at"] = datetime.utcnow().isoformat()
            await supabase.insert("recipient_lists", recipient_data)
        
        return {
            "success": True,
            "message": f"Recipients saved successfully",
            "count": len(recipients.recipients)
        }
        
    except Exception as e:
        logger.error(f"Save recipients error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save recipients")

@app.get("/api/recipients/load")
async def load_recipients(user_id: int = Depends(verify_token)):
    """Load user's recipient lists"""
    try:
        lists = await supabase.select("recipient_lists", filters={"user_id": user_id})
        
        result = []
        for lst in lists:
            result.append({
                "id": lst["id"],
                "list_name": lst["list_name"],
                "recipients": json.loads(lst["recipients"]),
                "created_at": lst["created_at"],
                "updated_at": lst["updated_at"],
                "count": len(json.loads(lst["recipients"]))
            })
        
        return {"success": True, "lists": result}
        
    except Exception as e:
        logger.error(f"Load recipients error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load recipients")

@app.delete("/api/recipients/delete/{list_id}")
async def delete_recipients(list_id: int, user_id: int = Depends(verify_token)):
    """Delete recipient list"""
    try:
        # Verify ownership
        lists = await supabase.select("recipient_lists", filters={"id": list_id})
        if not lists or lists[0]["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete list
        await supabase.delete("recipient_lists", {"id": list_id})
        
        return {"success": True, "message": "List deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete recipients error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete list")

# Settings endpoints
@app.post("/api/settings/save")
async def save_settings(settings: Dict[str, Any], user_id: int = Depends(verify_token)):
    """Save user settings"""
    try:
        # Check if settings exist
        existing = await supabase.select("user_settings", filters={"user_id": user_id})
        
        settings_data = {
            "user_id": user_id,
            "settings": json.dumps(settings),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if existing:
            await supabase.update("user_settings", settings_data, {"user_id": user_id})
        else:
            await supabase.insert("user_settings", settings_data)
        
        return {"success": True, "message": "Settings saved successfully"}
        
    except Exception as e:
        logger.error(f"Save settings error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save settings")

@app.get("/api/settings/load")
async def load_settings(user_id: int = Depends(verify_token)):
    """Load user settings"""
    try:
        settings = await supabase.select("user_settings", filters={"user_id": user_id})
        
        if settings:
            return {
                "success": True, 
                "settings": json.loads(settings[0]["settings"])
            }
        
        return {"success": True, "settings": {}}
        
    except Exception as e:
        logger.error(f"Load settings error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load settings")

# Campaign tracking
@app.post("/api/campaigns/create")
async def create_campaign(
    campaign_name: str = Form(...),
    total_emails: int = Form(...),
    user_id: int = Depends(verify_token)
):
    """Create new email campaign"""
    try:
        campaign_data = {
            "user_id": user_id,
            "campaign_name": campaign_name,
            "status": "pending",
            "total_emails": total_emails,
            "sent_emails": 0,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = await supabase.insert("email_campaigns", campaign_data)
        
        return {
            "success": True,
            "campaign_id": result[0]["id"] if result else None,
            "message": "Campaign created successfully"
        }
        
    except Exception as e:
        logger.error(f"Create campaign error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create campaign")

@app.get("/api/campaigns")
async def get_campaigns(user_id: int = Depends(verify_token)):
    """Get user's campaigns"""
    try:
        campaigns = await supabase.select("email_campaigns", filters={"user_id": user_id})
        return {"success": True, "campaigns": campaigns}
        
    except Exception as e:
        logger.error(f"Get campaigns error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get campaigns")

# Admin routes
@app.get("/admin", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin/login")
async def admin_login(request: Request, username: str = Form(), password: str = Form()):
    """Admin login"""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Create admin token
        token = jwt.encode({
            "username": username,
            "role": "admin",
            "exp": datetime.utcnow() + timedelta(hours=8)
        }, JWT_SECRET, algorithm="HS256")
        
        response = RedirectResponse(url="/admin/dashboard", status_code=302)
        response.set_cookie("admin_token", token, httponly=True, max_age=28800)
        return response
    
    return templates.TemplateResponse("admin_login.html", {
        "request": request, 
        "error": "Invalid admin credentials"
    })

@app.get("/admin/logout")
async def admin_logout():
    """Admin logout"""
    response = RedirectResponse(url="/admin", status_code=302)
    response.delete_cookie("admin_token")
    return response

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin: bool = Depends(verify_admin_session)):
    """Admin dashboard"""
    try:
        # Get all users with statistics
        users = await supabase.select("users")
        
        # Add days remaining calculation for each user
        for user in users:
            user["days_remaining"] = calculate_days_remaining(user["expires_at"])
            user["status"] = "expired" if user["days_remaining"] <= 0 else "active"
        
        # Get statistics
        total_users = len(users)
        active_users = len([u for u in users if u["days_remaining"] > 0])
        expired_users = total_users - active_users
        
        # Get recent campaigns
        campaigns = await supabase.select("email_campaigns")
        total_campaigns = len(campaigns)
        
        stats = {
            "total_users": total_users,
            "active_users": active_users,
            "expired_users": expired_users,
            "total_campaigns": total_campaigns
        }
        
        success_msg = request.query_params.get('success')
        error_msg = request.query_params.get('error')
        
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "users": users,
            "stats": stats,
            "success": success_msg,
            "error": error_msg
        })
        
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Dashboard error")

@app.post("/admin/users/add")
async def admin_add_user(
    request: Request,
    username: str = Form(),
    password: str = Form(),
    email: str = Form(""),
    subscription_type: str = Form("free"),
    expiration_days: int = Form(30),
    admin: bool = Depends(verify_admin_session)
):
    """Add new user (admin only)"""
    try:
        # Check if user exists
        existing = await supabase.select("users", filters={"username": username})
        if existing:
            return RedirectResponse(
                url="/admin/dashboard?error=Username already exists", 
                status_code=302
            )
        
        # Calculate expiration date
        expires_at = (datetime.utcnow() + timedelta(days=expiration_days)).isoformat()
        
        user_data = {
            "username": username,
            "hashed_password": hash_password(password),
            "email": email,
            "subscription_type": subscription_type,
            "expires_at": expires_at,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "total_emails_sent": 0
        }
        
        await supabase.insert("users", user_data)
        
        return RedirectResponse(
            url=f"/admin/dashboard?success=User '{username}' added successfully", 
            status_code=302
        )
        
    except Exception as e:
        logger.error(f"Admin add user error: {e}")
        return RedirectResponse(
            url=f"/admin/dashboard?error=Failed to add user: {str(e)}", 
            status_code=302
        )

@app.post("/admin/users/{user_id}/extend")
async def admin_extend_subscription(
    user_id: int, 
    extend_data: ExtendSubscription,
    admin: bool = Depends(verify_admin_session)
):
    """Extend user subscription"""
    try:
        users = await supabase.select("users", filters={"id": user_id})
        if not users:
            raise HTTPException(status_code=404, detail="User not found")
        
        current_expiry = datetime.fromisoformat(users[0]["expires_at"])
        new_expiry = current_expiry + timedelta(days=extend_data.days)
        
        await supabase.update("users", 
                            {"expires_at": new_expiry.isoformat()}, 
                            {"id": user_id})
        
        return {
            "success": True,
            "message": f"Subscription extended by {extend_data.days} days",
            "new_expiry": new_expiry.strftime("%Y-%m-%d")
        }
        
    except Exception as e:
        logger.error(f"Extend subscription error: {e}")
        raise HTTPException(status_code=500, detail="Failed to extend subscription")

@app.post("/admin/users/{user_id}/set-expiration")
async def admin_set_expiration(
    user_id: int,
    expiration_data: SetExpiration,
    admin: bool = Depends(verify_admin_session)
):
    """Set user expiration date"""
    try:
        expires_at = datetime.strptime(expiration_data.expiration_date, "%Y-%m-%d").isoformat()
        
        await supabase.update("users", {
            "expires_at": expires_at,
            "subscription_type": expiration_data.subscription_type,
            "is_active": True
        }, {"id": user_id})
        
        return {
            "success": True,
            "message": f"Expiration set to {expiration_data.expiration_date}",
            "subscription_type": expiration_data.subscription_type
        }
        
    except Exception as e:
        logger.error(f"Set expiration error: {e}")
        raise HTTPException(status_code=500, detail="Failed to set expiration")

@app.delete("/admin/users/{user_id}")
async def admin_delete_user(
    user_id: int, 
    admin: bool = Depends(verify_admin_session)
):
    """Delete user and all their data"""
    try:
        # Delete user's recipient lists
        await supabase.delete("recipient_lists", {"user_id": user_id})
        
        # Delete user's campaigns
        await supabase.delete("email_campaigns", {"user_id": user_id})
        
        # Delete user's settings
        await supabase.delete("user_settings", {"user_id": user_id})
        
        # Delete user
        await supabase.delete("users", {"id": user_id})
        
        return {"success": True, "message": "User deleted successfully"}
        
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

@app.get("/admin/users/{user_id}/data", response_class=HTMLResponse)
async def admin_view_user_data(
    user_id: int, 
    request: Request, 
    admin: bool = Depends(verify_admin_session)
):
    """View user's data"""
    try:
        # Get user info
        users = await supabase.select("users", filters={"id": user_id})
        if not users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = users[0]
        user["days_remaining"] = calculate_days_remaining(user["expires_at"])
        
        # Get user's recipient lists
        recipient_lists = await supabase.select("recipient_lists", filters={"user_id": user_id})
        for lst in recipient_lists:
            lst["recipients"] = json.loads(lst["recipients"])
            lst["count"] = len(lst["recipients"])
        
        # Get user's campaigns
        campaigns = await supabase.select("email_campaigns", filters={"user_id": user_id})
        
        # Get user's settings
        settings = await supabase.select("user_settings", filters={"user_id": user_id})
        user_settings = json.loads(settings[0]["settings"]) if settings else {}
        
        return templates.TemplateResponse("user_data.html", {
            "request": request,
            "user": user,
            "recipient_lists": recipient_lists,
            "campaigns": campaigns,
            "settings": user_settings
        })
        
    except Exception as e:
        logger.error(f"View user data error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load user data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
