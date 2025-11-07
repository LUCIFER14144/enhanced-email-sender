from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import jwt
import json
from datetime import datetime, timedelta
import logging
import httpx

# Configure logging FIRST
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import bcrypt, use fallback if not available
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logger.warning("bcrypt not available, using simple hash")

app = FastAPI(title="Enhanced Email Sender API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
        if not self.url or not self.key:
            logger.warning("Supabase credentials not configured - using mock mode with in-memory storage")
            self.mock_mode = True
            # In-memory storage
            self.mock_data = {"users": [], "email_campaigns": [], "recipient_lists": [], "user_settings": []}
            self.next_id = 1
        else:
            self.mock_mode = False
            self.headers = {
                "apikey": self.key,
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json"
            }
    
    async def select(self, table: str, columns: str = "*", filters: Dict = None):
        """Select data from Supabase table"""
        if self.mock_mode:
            data = self.mock_data.get(table, [])
            if filters:
                return [item for item in data if all(item.get(k) == v for k, v in filters.items())]
            return data
            
        url = f"{self.url}/rest/v1/{table}"
        params = {"select": columns}
        
        if filters:
            for key, value in filters.items():
                params[f"{key}"] = f"eq.{value}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params, timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                return []
        except Exception as e:
            logger.error(f"Supabase select error: {e}")
            return []
    
    async def insert(self, table: str, data: Dict):
        """Insert data into Supabase table"""
        if self.mock_mode:
            new_item = {"id": self.next_id, **data}
            self.next_id += 1
            if table not in self.mock_data:
                self.mock_data[table] = []
            self.mock_data[table].append(new_item)
            return [new_item]
            
        url = f"{self.url}/rest/v1/{table}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=data, timeout=10.0)
                if response.status_code in [200, 201]:
                    return response.json()
                raise HTTPException(status_code=400, detail="Insert failed")
        except Exception as e:
            logger.error(f"Supabase insert error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def update(self, table: str, data: Dict, filters: Dict):
        """Update data in Supabase table"""
        if self.mock_mode:
            items = self.mock_data.get(table, [])
            for item in items:
                if all(item.get(k) == v for k, v in filters.items()):
                    item.update(data)
            return [data]
            
        url = f"{self.url}/rest/v1/{table}"
        params = {}
        
        for key, value in filters.items():
            params[f"{key}"] = f"eq.{value}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(url, headers=self.headers, params=params, json=data, timeout=10.0)
                if response.status_code in [200, 201]:
                    return response.json()
                raise HTTPException(status_code=400, detail="Update failed")
        except Exception as e:
            logger.error(f"Supabase update error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def create_campaign(self, campaign_data: Dict):
        """Create a new campaign in Supabase"""
        return await self.insert("campaigns", campaign_data)
    
    async def delete(self, table: str, filters: Dict):
        """Delete data from Supabase table"""
        if self.mock_mode:
            items = self.mock_data.get(table, [])
            self.mock_data[table] = [item for item in items if not all(item.get(k) == v for k, v in filters.items())]
            return True
            
        url = f"{self.url}/rest/v1/{table}"
        params = {}
        
        for key, value in filters.items():
            params[f"{key}"] = f"eq.{value}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, headers=self.headers, params=params, timeout=10.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Supabase delete error: {e}")
            return False

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
    """Hash password using bcrypt or fallback"""
    if BCRYPT_AVAILABLE:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    else:
        # Simple fallback hash (not for production!)
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    if BCRYPT_AVAILABLE:
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except:
            # Fallback comparison
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest() == hashed
    else:
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest() == hashed

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

@app.get("/api/admin/campaigns")
async def list_campaigns(request: Request):
    """List all email campaigns"""
    # Verify admin session
    await verify_admin_session(request)
    
    try:
        campaigns = await supabase.select("campaigns", "*")
        if not campaigns:
            return []
        return campaigns
    except Exception as e:
        logger.error(f"Error listing campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing campaigns: {str(e)}")

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
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Login - Enhanced Email Sender</title>
        <style>
            body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .login-box { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); width: 350px; }
            h2 { text-align: center; color: #333; margin-bottom: 30px; }
            input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
            button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #5568d3; }
            .error { color: red; text-align: center; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>🔐 Admin Login</h2>
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
    
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Login - Enhanced Email Sender</title>
        <style>
            body { font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .login-box { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); width: 350px; }
            h2 { text-align: center; color: #333; margin-bottom: 30px; }
            input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
            button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #5568d3; }
            .error { color: red; text-align: center; margin-top: 10px; background: #ffe6e6; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>🔐 Admin Login</h2>
            <div class="error">❌ Invalid admin credentials</div>
            <form method="post" action="/admin/login">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
        </div>
    </body>
    </html>
    """)

@app.get("/admin/logout")
async def admin_logout():
    """Admin logout"""
    response = RedirectResponse(url="/admin", status_code=302)
    response.delete_cookie("admin_token")
    return response

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin: bool = Depends(verify_admin_session)):
    """Admin dashboard with full user management"""
    try:
        # Fetch all users
        users = await supabase.select("users") or []
        
        # Calculate days remaining for each user
        for user in users:
            if user.get("expires_at"):
                try:
                    expiry = datetime.fromisoformat(user["expires_at"].replace('Z', '+00:00'))
                    days_left = (expiry - datetime.utcnow()).days
                    user["days_remaining"] = max(0, days_left)
                except:
                    user["days_remaining"] = 0
            else:
                user["days_remaining"] = 0
        
        # Calculate stats
        total_users = len(users)
        active_users = sum(1 for u in users if u.get("is_active") and u.get("days_remaining", 0) > 0)
        expired_users = sum(1 for u in users if u.get("days_remaining", 0) <= 0)
        
        campaigns = await supabase.select("email_campaigns") or []
        total_campaigns = len(campaigns)
        
        # Get success/error messages from query params
        success_msg = request.query_params.get('success', '')
        error_msg = request.query_params.get('error', '')
        
        # Build users HTML rows
        users_html = ""
        for user in users:
            sub_type = user.get("subscription_type", "free")
            badge_class = "success" if sub_type == "premium" else ("primary" if sub_type == "enterprise" else "warning")
            days_remaining = user.get("days_remaining", 0)
            days_badge = "danger" if days_remaining <= 0 else ("warning" if days_remaining <= 7 else "success")
            is_active = user.get("is_active") and days_remaining > 0
            status_badge = "success" if is_active else "danger"
            status_text = "Active" if is_active else "Inactive"
            expires_at = user.get("expires_at", "N/A")[:10] if user.get("expires_at") else "N/A"
            
            users_html += f"""
            <tr>
                <td>{user.get("id")}</td>
                <td><strong>{user.get("username")}</strong></td>
                <td>{user.get("email") or "N/A"}</td>
                <td><span class="badge badge-{badge_class}">{sub_type.title()}</span></td>
                <td>{expires_at}</td>
                <td><span class="badge badge-{days_badge}">{days_remaining} days</span></td>
                <td><span class="badge badge-{status_badge}">{status_text}</span></td>
                <td>
                    <div class="actions">
                        <button onclick="extendSubscription({user.get('id')})" class="btn btn-warning btn-sm">➕ Extend</button>
                        <button onclick="setExpiration({user.get('id')})" class="btn btn-primary btn-sm">📅 Set Date</button>
                        <button onclick="deleteUser({user.get('id')}, '{user.get('username')}')" class="btn btn-danger btn-sm">🗑️ Delete</button>
                    </div>
                </td>
            </tr>
            """
        
        alert_html = ""
        if success_msg:
            alert_html = f'<div class="alert alert-success">✅ {success_msg}</div>'
        if error_msg:
            alert_html = f'<div class="alert alert-danger">❌ {error_msg}</div>'
        
        return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Enhanced Email Sender</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f8f9fa; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header-content {{ max-width: 1200px; margin: 0 auto; padding: 0 2rem; display: flex; justify-content: space-between; align-items: center; }}
        .header h1 {{ font-size: 1.8rem; font-weight: 600; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .card {{ background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; box-shadow: 0 2px 15px rgba(0,0,0,0.08); border: 1px solid #e9ecef; }}
        .card h2 {{ color: #495057; margin-bottom: 1rem; font-size: 1.3rem; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .stat-card {{ background: white; padding: 1.5rem; border-radius: 12px; text-align: center; box-shadow: 0 2px 15px rgba(0,0,0,0.08); border-left: 4px solid; }}
        .stat-card.users {{ border-left-color: #28a745; }}
        .stat-card.active {{ border-left-color: #007bff; }}
        .stat-card.expired {{ border-left-color: #dc3545; }}
        .stat-card.campaigns {{ border-left-color: #ffc107; }}
        .stat-number {{ font-size: 2rem; font-weight: bold; color: #495057; }}
        .stat-label {{ color: #6c757d; font-size: 0.9rem; margin-top: 0.5rem; }}
        .add-user-form {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; align-items: end; margin-bottom: 1.5rem; }}
        .form-group {{ display: flex; flex-direction: column; }}
        .form-group label {{ margin-bottom: 0.25rem; font-weight: 500; color: #495057; font-size: 0.9rem; }}
        .form-group input, .form-group select {{ padding: 0.5rem; border: 1px solid #ced4da; border-radius: 6px; font-size: 0.9rem; }}
        .table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        .table th, .table td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #dee2e6; }}
        .table th {{ background: #f8f9fa; font-weight: 600; color: #495057; font-size: 0.9rem; }}
        .table tbody tr:hover {{ background: #f8f9fa; }}
        .badge {{ padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-danger {{ background: #f8d7da; color: #721c24; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .badge-primary {{ background: #cce5ff; color: #004085; }}
        .btn {{ padding: 0.5rem 1rem; border: none; border-radius: 6px; font-size: 0.9rem; cursor: pointer; text-decoration: none; display: inline-block; transition: all 0.3s ease; }}
        .btn-sm {{ padding: 0.25rem 0.5rem; font-size: 0.8rem; }}
        .btn-success {{ background: #28a745; color: white; }}
        .btn-success:hover {{ background: #218838; }}
        .btn-primary {{ background: #007bff; color: white; }}
        .btn-primary:hover {{ background: #0056b3; }}
        .btn-warning {{ background: #ffc107; color: #212529; }}
        .btn-warning:hover {{ background: #e0a800; }}
        .btn-danger {{ background: #dc3545; color: white; }}
        .btn-danger:hover {{ background: #c82333; }}
        .btn-outline {{ background: transparent; color: white; border: 1px solid white; }}
        .btn-outline:hover {{ background: white; color: #667eea; }}
        .alert {{ padding: 0.75rem 1rem; margin-bottom: 1rem; border: 1px solid transparent; border-radius: 6px; }}
        .alert-success {{ color: #155724; background-color: #d4edda; border-color: #c3e6cb; }}
        .alert-danger {{ color: #721c24; background-color: #f8d7da; border-color: #f5c6cb; }}
        .actions {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div>
                <h1>📧 Enhanced Email Sender</h1>
                <p>Administration Dashboard</p>
            </div>
            <div><a href="/admin/logout" class="btn btn-outline">🚪 Logout</a></div>
        </div>
    </div>
    <div class="container">
        {alert_html}
        <div class="stats-grid">
            <div class="stat-card users"><div class="stat-number">{total_users}</div><div class="stat-label">Total Users</div></div>
            <div class="stat-card active"><div class="stat-number">{active_users}</div><div class="stat-label">Active Users</div></div>
            <div class="stat-card expired"><div class="stat-number">{expired_users}</div><div class="stat-label">Expired Users</div></div>
            <div class="stat-card campaigns"><div class="stat-number">{total_campaigns}</div><div class="stat-label">Total Campaigns</div></div>
        </div>
        <div class="card">
            <h2>➕ Add New User</h2>
            <form method="post" action="/admin/users/add" class="add-user-form">
                <div class="form-group"><label for="username">Username</label><input type="text" id="username" name="username" required></div>
                <div class="form-group"><label for="password">Password</label><input type="password" id="password" name="password" required></div>
                <div class="form-group"><label for="email">Email</label><input type="email" id="email" name="email"></div>
                <div class="form-group"><label for="subscription_type">Subscription</label>
                    <select id="subscription_type" name="subscription_type">
                        <option value="free">Free</option>
                        <option value="premium">Premium</option>
                        <option value="enterprise">Enterprise</option>
                    </select>
                </div>
                <div class="form-group"><label for="expiration_days">Days</label><input type="number" id="expiration_days" name="expiration_days" value="30" min="1" max="3650"></div>
                <div class="form-group"><button type="submit" class="btn btn-success">Add User</button></div>
            </form>
        </div>
        <div class="card">
            <h2>👥 Registered Users ({total_users})</h2>
            <div class="table-responsive">
                <table class="table">
                    <thead><tr><th>ID</th><th>Username</th><th>Email</th><th>Subscription</th><th>Expires</th><th>Days Left</th><th>Status</th><th>Actions</th></tr></thead>
                    <tbody>{users_html}</tbody>
                </table>
            </div>
        </div>
    </div>
    <script>
        function extendSubscription(userId) {{
            const days = prompt("How many days to extend the subscription?", "30");
            if (days && parseInt(days) > 0) {{
                fetch(`/admin/users/${{userId}}/extend`, {{
                    method: 'POST', headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{days: parseInt(days)}})
                }})
                .then(response => response.json())
                .then(data => {{ if (data.success) {{ alert(data.message); location.reload(); }} else {{ alert('Error: ' + (data.detail || 'Failed')); }} }})
                .catch(error => alert('Error: ' + error.message));
            }}
        }}
        function setExpiration(userId) {{
            const date = prompt("Set expiration date (YYYY-MM-DD):", "2025-12-31");
            const subscriptionType = prompt("Subscription type:", "premium");
            if (date && subscriptionType) {{
                fetch(`/admin/users/${{userId}}/set-expiration`, {{
                    method: 'POST', headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{expiration_date: date, subscription_type: subscriptionType}})
                }})
                .then(response => response.json())
                .then(data => {{ if (data.success) {{ alert(data.message); location.reload(); }} else {{ alert('Error: ' + (data.detail || 'Failed')); }} }})
                .catch(error => alert('Error: ' + error.message));
            }}
        }}
        function deleteUser(userId, username) {{
            if (confirm(`Delete user "${{username}}"?\\n\\nThis will delete all their data and cannot be undone!`)) {{
                fetch(`/admin/users/${{userId}}`, {{method: 'DELETE'}})
                .then(response => response.json())
                .then(data => {{ if (data.success) {{ alert(data.message); location.reload(); }} else {{ alert('Error: ' + (data.detail || 'Failed')); }} }})
                .catch(error => alert('Error: ' + error.message));
            }}
        }}
    </script>
</body>
</html>
        """)
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        return HTMLResponse(f"""
        <html><body style="font-family: Arial; padding: 50px; text-align: center;">
        <h1>⚠️ Dashboard Error</h1>
        <p>Error loading dashboard: {str(e)}</p>
        <p><a href="/admin/logout">Logout</a></p>
        </body></html>
        """)

@app.post("/admin/users/add")
async def admin_add_user(
    request: Request,
    username: str = Form(),
    password: str = Form(),
    email: str = Form(""),
    subscription_type: str = Form("free"),
    expiration_days: int = Form(30)
):
    """Add new user (admin only)"""
    try:
        # Verify admin session manually to avoid dependency issues
        token = request.cookies.get("admin_token")
        if not token:
            return RedirectResponse(url="/admin?error=Not authenticated", status_code=302)
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            if payload.get("role") != "admin":
                return RedirectResponse(url="/admin?error=Not authorized", status_code=302)
        except:
            return RedirectResponse(url="/admin?error=Invalid session", status_code=302)
        
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
            "email": email or None,
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
    request: Request
):
    """Extend user subscription"""
    try:
        # Verify admin
        token = request.cookies.get("admin_token")
        if not token:
            return JSONResponse({"success": False, "detail": "Not authenticated"}, status_code=401)
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            if payload.get("role") != "admin":
                return JSONResponse({"success": False, "detail": "Not authorized"}, status_code=403)
        except:
            return JSONResponse({"success": False, "detail": "Invalid session"}, status_code=401)
        
        # Get request body
        body = await request.json()
        days = body.get("days", 30)
        
        users = await supabase.select("users", filters={"id": user_id})
        if not users:
            return JSONResponse({"success": False, "detail": "User not found"}, status_code=404)
        
        current_expiry = datetime.fromisoformat(users[0]["expires_at"].replace('Z', '+00:00'))
        new_expiry = current_expiry + timedelta(days=days)
        
        await supabase.update("users", 
                            {"expires_at": new_expiry.isoformat()}, 
                            {"id": user_id})
        
        return {
            "success": True,
            "message": f"Subscription extended by {days} days",
            "new_expiry": new_expiry.strftime("%Y-%m-%d")
        }
        
    except Exception as e:
        logger.error(f"Extend subscription error: {e}")
        return JSONResponse({"success": False, "detail": str(e)}, status_code=500)

@app.post("/admin/users/{user_id}/set-expiration")
async def admin_set_expiration(
    user_id: int,
    request: Request
):
    """Set user expiration date"""
    try:
        # Verify admin
        token = request.cookies.get("admin_token")
        if not token:
            return JSONResponse({"success": False, "detail": "Not authenticated"}, status_code=401)
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            if payload.get("role") != "admin":
                return JSONResponse({"success": False, "detail": "Not authorized"}, status_code=403)
        except:
            return JSONResponse({"success": False, "detail": "Invalid session"}, status_code=401)
        
        # Get request body
        body = await request.json()
        expiration_date = body.get("expiration_date")
        subscription_type = body.get("subscription_type", "premium")
        
        expires_at = datetime.strptime(expiration_date, "%Y-%m-%d").isoformat()
        
        await supabase.update("users", {
            "expires_at": expires_at,
            "subscription_type": subscription_type,
            "is_active": True
        }, {"id": user_id})
        
        return {
            "success": True,
            "message": f"Expiration set to {expiration_date}",
            "subscription_type": subscription_type
        }
        
    except Exception as e:
        logger.error(f"Set expiration error: {e}")
        return JSONResponse({"success": False, "detail": str(e)}, status_code=500)

@app.delete("/admin/users/{user_id}")
async def admin_delete_user(
    user_id: int,
    request: Request
):
    """Delete user and all their data"""
    try:
        # Verify admin
        token = request.cookies.get("admin_token")
        if not token:
            return JSONResponse({"success": False, "detail": "Not authenticated"}, status_code=401)
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            if payload.get("role") != "admin":
                return JSONResponse({"success": False, "detail": "Not authorized"}, status_code=403)
        except:
            return JSONResponse({"success": False, "detail": "Invalid session"}, status_code=401)
        
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
        return JSONResponse({"success": False, "detail": str(e)}, status_code=500)

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
