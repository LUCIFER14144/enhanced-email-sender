from fastapi import FastAPI
import os
from datetime import datetime

app = FastAPI()

# Mount admin routes
try:
    from .new_admin import app as admin_app
    app.mount("/admin", admin_app)
except ImportError:
    print("Warning: Admin module not found or could not be loaded")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }