from fastapi import FastAPI, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import jwt
import os
from datetime import datetime, timedelta

app = FastAPI()

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

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
                    body { font-family: Arial; margin: 40px; }
                    .header { display: flex; justify-content: space-between; align-items: center; }
                    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
                    .stat-card { padding: 20px; background: #f5f5f5; border-radius: 8px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Admin Dashboard</h1>
                    <a href="/admin/logout">Logout</a>
                </div>
                <div class="stats">
                    <div class="stat-card">
                        <h3>Total Users</h3>
                        <p>2</p>
                    </div>
                    <div class="stat-card">
                        <h3>Active Users</h3>
                        <p>2</p>
                    </div>
                    <div class="stat-card">
                        <h3>Total Emails Sent</h3>
                        <p>0</p>
                    </div>
                </div>
                <h2>Quick Actions</h2>
                <ul>
                    <li><a href="/admin/users">Manage Users</a></li>
                    <li><a href="/admin/campaigns">Email Campaigns</a></li>
                    <li><a href="/admin/settings">System Settings</a></li>
                </ul>
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