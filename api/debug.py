#!/usr/bin/env python3
"""
Minimal health check version for debugging Vercel deployment
This version works without database connections to test basic functionality
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

# Create FastAPI app
app = FastAPI(
    title="Enhanced Email Sender API",
    description="Cloud-enabled email sender with user management",
    version="1.0.0"
)

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "message": "Enhanced Email Sender API",
        "status": "active",
        "version": "1.0.0",
        "environment": "production"
    }

@app.get("/debug")
async def debug_info():
    """Debug endpoint to check environment"""
    env_vars = {
        "SUPABASE_URL": "✅ Set" if os.getenv("SUPABASE_URL") else "❌ Missing",
        "SUPABASE_ANON_KEY": "✅ Set" if os.getenv("SUPABASE_ANON_KEY") else "❌ Missing",
        "JWT_SECRET": "✅ Set" if os.getenv("JWT_SECRET") else "❌ Missing",
        "ADMIN_USERNAME": "✅ Set" if os.getenv("ADMIN_USERNAME") else "❌ Missing",
        "ADMIN_PASSWORD": "✅ Set" if os.getenv("ADMIN_PASSWORD") else "❌ Missing",
    }
    
    return {
        "message": "Debug Information",
        "environment_variables": env_vars,
        "python_version": "3.12",
        "status": "debugging"
    }

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {
        "message": "Test endpoint working",
        "status": "success"
    }

# For Vercel deployment
def handler(request):
    return app(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)