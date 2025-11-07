from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import os
import json
from datetime import datetime

app = FastAPI(title="Enhanced Email Sender API", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "Enhanced Email Sender API",
        "status": "active",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

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
async def admin_login():
    return {"message": "Admin login endpoint", "status": "working"}

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

# Test endpoint
@app.get("/test")
async def test():
    return {
        "message": "Test endpoint working perfectly!",
        "status": "success",
        "environment": "production" if os.getenv("VERCEL") else "development"
    }