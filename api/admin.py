from fastapi import FastAPI, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import jwt
import os
from datetime import datetime, timedelta

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
from pydantic import BaseModel
from typing import Optional

class AdminUser(BaseModel):
    username: str
    email: str
    password: str
    subscription_tier: str = "free"
    daily_email_limit: int = 100
    subscription_end: str

# Error Handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith("/admin/"):
        return RedirectResponse(url="/admin/login")
    return JSONResponse(
        status_code=404,
        content={"detail": "Not Found"}
    )

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Admin Routes
@app.get("/admin")
async def admin_root(request: Request):
    """Redirect to admin dashboard if authenticated, otherwise to login"""
    token = request.cookies.get("admin_token")
    if token:
        try:
            jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return RedirectResponse(url="/admin/dashboard")
        except:
            pass
    return RedirectResponse(url="/admin/login")

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard page"""
    token = request.cookies.get("admin_token")
    if not token:
        return RedirectResponse(url="/admin/login")
    
    try:
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Admin Dashboard</title>
                <style>
                    body { font-family: Arial; margin: 20px; }
                    .header { padding: 20px 0; border-bottom: 1px solid #eee; }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .btn { 
                        padding: 10px 20px; 
                        background: #4CAF50; 
                        color: white; 
                        border: none; 
                        cursor: pointer;
                        margin: 5px;
                        display: inline-block;
                        text-decoration: none;
                    }
                    .btn:hover { background: #45a049; }
                    .section { margin: 20px 0; }
                    .users-table, .campaigns { margin-top: 20px; }
                    .settings-panel { margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="container">
                        <h1>Admin Dashboard</h1>
                        <a href="/admin/logout" class="btn" style="float: right;">Logout</a>
                    </div>
                </div>
                <div class="container">
                    <div class="section">
                        <h2>User Management</h2>
                        <button class="btn" onclick="document.getElementById('addUserModal').style.display='block'">Add New User</button>
                        <div class="users-table">
                            <!-- Users will be loaded here -->
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>Email Campaigns</h2>
                        <button class="btn" onclick="document.getElementById('createCampaignModal').style.display='block'">Create New Campaign</button>
                        <div class="campaigns">
                            <!-- Campaigns will be loaded here -->
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>System Configuration</h2>
                        <button class="btn" onclick="document.getElementById('systemSettingsModal').style.display='block'">System Settings</button>
                        <div class="settings-panel">
                            <!-- Settings will be loaded here -->
                        </div>
                    </div>
                </div>
                
                <!-- Add modals here -->
                <!-- Your existing modals code will be here -->
            </body>
        </html>
        """)
    except:
        return RedirectResponse(url="/admin/login")

# User Management Routes
@app.post("/api/admin/users")
async def create_user(user: AdminUser, request: Request):
    """Create a new user"""
    # Verify admin session
    token = request.cookies.get("admin_token")
    if not token:
        raise HTTPException(status_code=401, detail="Admin authentication required")
    
    try:
        # Verify token
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")

        # Hash the password
        import bcrypt
        hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
        
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

        # Insert into database using Supabase
        from main import supabase
        existing_user = await supabase.select("users", "*", {"username": user.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        result = await supabase.insert("users", user_data)
        
        # Log user creation
        await supabase.insert("usage_logs", {
            "user_id": result[0]["id"],
            "action": "user_created",
            "details": f"User created by admin with subscription tier: {user.subscription_tier}"
        })
        
        return {"message": "User created successfully", "user_id": result[0]["id"]}
        
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid admin token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Admin Login</title>
            <style>
                body { font-family: Arial; margin: 40px auto; max-width: 400px; }
                .form-group { margin-bottom: 15px; }
                input { width: 100%; padding: 8px; margin-top: 5px; }
                button { width: 100%; padding: 10px; background: #4CAF50; color: white; border: none; }
            </style>
        </head>
        <body>
            <h1>Admin Login</h1>
            <form method="post" action="/admin/login">
                <div class="form-group">
                    <label>Username:</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Password:</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit">Login</button>
            </form>
        </body>
    </html>
    """)

@app.post("/admin/login")
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
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
        response = RedirectResponse(url="/admin/dashboard", status_code=302)
        response.set_cookie(key="admin_token", value=token, httponly=True)
        return response
    
    return HTMLResponse(
        content="Invalid credentials. <a href='/admin/login'>Try again</a>",
        status_code=401
    )

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    token = request.cookies.get("admin_token")
    if not token:
        return RedirectResponse(url="/admin/login")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403)
        
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Admin Dashboard</title>
                <style>
                    body { font-family: Arial; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
                    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
                    .stat-card { padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #4CAF50; }
                    .quick-actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 30px; }
                    .action-card { background: white; padding: 20px; border-radius: 8px; border: 1px solid #ddd; }
                    .action-card h3 { margin-top: 0; color: #333; }
                    .btn { display: inline-block; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 10px; }
                    .btn:hover { background: #45a049; }
                    .logout { padding: 8px 16px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px; }
                    .logout:hover { background: #c82333; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Admin Dashboard</h1>
                        <a href="/admin/logout" class="logout">Logout</a>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-card">
                            <h3>Total Users</h3>
                            <p style="font-size: 24px; font-weight: bold;">2</p>
                        </div>
                        <div class="stat-card">
                            <h3>Active Users</h3>
                            <p style="font-size: 24px; font-weight: bold;">2</p>
                        </div>
                        <div class="stat-card">
                            <h3>Total Emails Sent</h3>
                            <p style="font-size: 24px; font-weight: bold;">0</p>
                        </div>
                    </div>
                    
                    <div class="quick-actions">
                        <div class="action-card">
                            <h3>User Management</h3>
                            <p>Manage user accounts, subscriptions, and permissions</p>
                            <a href="/admin/users" class="btn">Manage Users</a>
                        </div>
                        <div class="action-card">
                            <h3>Email Campaigns</h3>
                            <p>View and manage email campaigns and analytics</p>
                            <a href="/admin/campaigns" class="btn">View Campaigns</a>
                        </div>
                        <div class="action-card">
                            <h3>System Settings</h3>
                            <p>Configure system settings and preferences</p>
                            <a href="/admin/settings" class="btn">Configure</a>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """)
    except:
        return RedirectResponse(url="/admin/login")

@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request):
    token = request.cookies.get("admin_token")
    if not token:
        return RedirectResponse(url="/admin/login")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if payload.get("role") != "admin":
            return RedirectResponse(url="/admin/login")
        
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
            <head>
                <title>User Management - Admin Dashboard</title>
                <style>
                    body { font-family: Arial; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
                    .btn { display: inline-block; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }
                    .btn:hover { background: #45a049; }
                    .back-btn { background: #6c757d; }
                    .back-btn:hover { background: #5a6268; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                    th { background: #f8f9fa; }
                    .user-actions { display: flex; gap: 10px; }
                    .edit-btn { background: #007bff; }
                    .delete-btn { background: #dc3545; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>User Management</h1>
                        <a href="/admin/dashboard" class="btn back-btn">Back to Dashboard</a>
                    </div>
                    
                    <button class="btn" onclick="document.getElementById('addUserModal').style.display='block'">Add New User</button>
                    
                    <!-- Add User Modal -->
                    <div id="addUserModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5);">
                        <div style="background: white; margin: 10% auto; padding: 20px; width: 50%; border-radius: 8px;">
                            <h2>Add New User</h2>
                            <form onsubmit="return submitNewUser(event)">
                                <div class="form-group">
                                    <label>Username:</label>
                                    <input type="text" id="newUsername" required>
                                </div>
                                <div class="form-group">
                                    <label>Email:</label>
                                    <input type="email" id="newEmail" required>
                                </div>
                                <div class="form-group">
                                    <label>Password:</label>
                                    <input type="password" id="newPassword" required>
                                </div>
                                <div class="form-group">
                                    <label>Subscription Tier:</label>
                                    <select id="newSubscriptionTier">
                                        <option value="free">Free</option>
                                        <option value="premium">Premium</option>
                                        <option value="enterprise">Enterprise</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Daily Email Limit:</label>
                                    <input type="number" id="newDailyLimit" value="100" required>
                                </div>
                                <div style="margin-top: 20px;">
                                    <button type="submit" class="btn">Add User</button>
                                    <button type="button" class="btn" style="background: #dc3545;" onclick="document.getElementById('addUserModal').style.display='none'">Cancel</button>
                                </div>
                            </form>
                        </div>
                    </div>

                    <script>
                    async function submitNewUser(event) {
                        event.preventDefault();
                        const userData = {
                            username: document.getElementById('newUsername').value,
                            email: document.getElementById('newEmail').value,
                            password: document.getElementById('newPassword').value,
                            subscription_tier: document.getElementById('newSubscriptionTier').value,
                            daily_email_limit: parseInt(document.getElementById('newDailyLimit').value)
                        };
                        
                        try {
                            const response = await fetch('/api/admin/users', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify(userData)
                            });
                            
                            if (response.ok) {
                                alert('User added successfully!');
                                document.getElementById('addUserModal').style.display = 'none';
                                location.reload();
                            } else {
                                const data = await response.json();
                                alert(data.detail || 'Error adding user');
                            }
                        } catch (error) {
                            alert('Error adding user: ' + error.message);
                        }
                    }
                    </script>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>Email</th>
                                <th>Subscription</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>admin</td>
                                <td>admin@emailsender.com</td>
                                <td>admin</td>
                                <td>Active</td>
                                <td class="user-actions">
                                    <a href="#" class="btn edit-btn" onclick="alert('Edit functionality coming soon!')">Edit</a>
                                    <a href="#" class="btn delete-btn" onclick="alert('Delete functionality coming soon!')">Delete</a>
                                </td>
                            </tr>
                            <tr>
                                <td>demo</td>
                                <td>demo@example.com</td>
                                <td>free</td>
                                <td>Active</td>
                                <td class="user-actions">
                                    <a href="#" class="btn edit-btn" onclick="alert('Edit functionality coming soon!')">Edit</a>
                                    <a href="#" class="btn delete-btn" onclick="alert('Delete functionality coming soon!')">Delete</a>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </body>
        </html>
        """)
    except:
        return RedirectResponse(url="/admin/login")

@app.get("/admin/campaigns", response_class=HTMLResponse)
async def admin_campaigns(request: Request):
    token = request.cookies.get("admin_token")
    if not token:
        return RedirectResponse(url="/admin/login")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403)
        
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
            <head>
                <title>Email Campaigns - Admin Dashboard</title>
                <style>
                    body { font-family: Arial; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
                    .btn { display: inline-block; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }
                    .btn:hover { background: #45a049; }
                    .back-btn { background: #6c757d; }
                    .back-btn:hover { background: #5a6268; }
                    .campaigns { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
                    .campaign-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #ddd; }
                    .campaign-stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 15px; }
                    .stat { background: white; padding: 10px; border-radius: 5px; text-align: center; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Email Campaigns</h1>
                        <a href="/admin/dashboard" class="btn back-btn">Back to Dashboard</a>
                    </div>
                    
                    <button class="btn" onclick="document.getElementById('createCampaignModal').style.display='block'">Create New Campaign</button>
                    
                    <!-- Create Campaign Modal -->
                    <div id="createCampaignModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5);">
                        <div style="background: white; margin: 10% auto; padding: 20px; width: 60%; border-radius: 8px;">
                            <h2>Create New Campaign</h2>
                            <form onsubmit="return submitNewCampaign(event)">
                                <div class="form-group">
                                    <label>Campaign Name:</label>
                                    <input type="text" id="campaignName" required>
                                </div>
                                <div class="form-group">
                                    <label>Template:</label>
                                    <select id="templateType" onchange="updateTemplateFields()">
                                        <option value="welcome">Welcome Email</option>
                                        <option value="newsletter">Newsletter</option>
                                        <option value="custom">Custom Template</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Subject:</label>
                                    <input type="text" id="emailSubject" required>
                                </div>
                                <div class="form-group">
                                    <label>Email Content:</label>
                                    <textarea id="emailContent" rows="6" style="width: 100%;" required></textarea>
                                </div>
                                <div class="form-group">
                                    <label>Recipients List:</label>
                                    <select id="recipientsList">
                                        <option value="all">All Users</option>
                                        <option value="free">Free Users</option>
                                        <option value="premium">Premium Users</option>
                                    </select>
                                </div>
                                <div style="margin-top: 20px;">
                                    <button type="submit" class="btn">Create Campaign</button>
                                    <button type="button" class="btn" style="background: #dc3545;" onclick="document.getElementById('createCampaignModal').style.display='none'">Cancel</button>
                                </div>
                            </form>
                        </div>
                    </div>

                    <script>
                    function updateTemplateFields() {
                        const templateType = document.getElementById('templateType').value;
                        const subjectField = document.getElementById('emailSubject');
                        const contentField = document.getElementById('emailContent');
                        
                        switch(templateType) {
                            case 'welcome':
                                subjectField.value = 'Welcome to Enhanced Email Sender!';
                                contentField.value = 'Dear {username},\n\nWelcome to Enhanced Email Sender! We\'re excited to have you on board.';
                                break;
                            case 'newsletter':
                                subjectField.value = 'Your Monthly Newsletter';
                                contentField.value = 'Hi {username},\n\nHere\'s your monthly update from Enhanced Email Sender.';
                                break;
                            case 'custom':
                                subjectField.value = '';
                                contentField.value = '';
                                break;
                        }
                    }

                    async function submitNewCampaign(event) {
                        event.preventDefault();
                        const campaignData = {
                            name: document.getElementById('campaignName').value,
                            template_type: document.getElementById('templateType').value,
                            subject: document.getElementById('emailSubject').value,
                            content: document.getElementById('emailContent').value,
                            recipients: document.getElementById('recipientsList').value
                        };
                        
                        try {
                            const response = await fetch('/api/admin/campaigns', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify(campaignData)
                            });
                            
                            if (response.ok) {
                                alert('Campaign created successfully!');
                                document.getElementById('createCampaignModal').style.display = 'none';
                                location.reload();
                            } else {
                                const data = await response.json();
                                alert(data.detail || 'Error creating campaign');
                            }
                        } catch (error) {
                            alert('Error creating campaign: ' + error.message);
                        }
                    }
                    </script>
                    
                    <div class="campaigns">
                        <div class="campaign-card">
                            <h3>Welcome Campaign</h3>
                            <p>Status: Active</p>
                            <div class="campaign-stats">
                                <div class="stat">
                                    <strong>0</strong>
                                    <div>Sent</div>
                                </div>
                                <div class="stat">
                                    <strong>0%</strong>
                                    <div>Open Rate</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="campaign-card">
                            <h3>Newsletter</h3>
                            <p>Status: Draft</p>
                            <div class="campaign-stats">
                                <div class="stat">
                                    <strong>0</strong>
                                    <div>Sent</div>
                                </div>
                                <div class="stat">
                                    <strong>0%</strong>
                                    <div>Open Rate</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """)
    except:
        return RedirectResponse(url="/admin/login")

@app.get("/admin/settings", response_class=HTMLResponse)
async def admin_settings(request: Request):
    token = request.cookies.get("admin_token")
    if not token:
        return RedirectResponse(url="/admin/login")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403)
        
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
            <head>
                <title>System Settings - Admin Dashboard</title>
                <style>
                    body { font-family: Arial; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
                    .btn { display: inline-block; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; }
                    .btn:hover { background: #45a049; }
                    .back-btn { background: #6c757d; }
                    .back-btn:hover { background: #5a6268; }
                    .settings-group { margin-bottom: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; }
                    .form-group { margin-bottom: 15px; }
                    label { display: block; margin-bottom: 5px; font-weight: bold; }
                    input, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>System Settings</h1>
                        <a href="/admin/dashboard" class="btn back-btn">Back to Dashboard</a>
                    </div>
                    
                    <div class="settings-group">
                        <h2>Email Settings</h2>
                        <div class="form-group">
                            <label>Daily Email Limit</label>
                            <input type="number" value="100" onchange="alert('Save functionality coming soon!')">
                        </div>
                        <div class="form-group">
                            <label>SMTP Server</label>
                            <input type="text" value="smtp.example.com" onchange="alert('Save functionality coming soon!')">
                        </div>
                    </div>
                    
                    <div class="settings-group">
                        <h2>Subscription Settings</h2>
                        <div class="form-group">
                            <label>Free Trial Duration (days)</label>
                            <input type="number" value="30" onchange="alert('Save functionality coming soon!')">
                        </div>
                        <div class="form-group">
                            <label>Default Subscription Tier</label>
                            <select onchange="alert('Save functionality coming soon!')">
                                <option>Free</option>
                                <option>Premium</option>
                                <option>Enterprise</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="settings-group">
                        <h2>Security Settings</h2>
                        <div class="form-group">
                            <label>Session Timeout (minutes)</label>
                            <input type="number" value="60" onchange="alert('Save functionality coming soon!')">
                        </div>
                        <div class="form-group">
                            <label>Maximum Login Attempts</label>
                            <input type="number" value="5" onchange="alert('Save functionality coming soon!')">
                        </div>
                    </div>
                    
                    <a href="#" class="btn" onclick="alert('Save all settings functionality coming soon!')">Save All Settings</a>
                </div>
            </body>
        </html>
        """)
    except:
        return RedirectResponse(url="/admin/login")

@app.get("/admin/logout")
async def admin_logout():
    response = RedirectResponse(url="/admin/login")
    response.delete_cookie("admin_token")
    return response