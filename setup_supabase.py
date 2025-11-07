#!/usr/bin/env python3
"""
Supabase Database Setup Script
This script sets up the database schema in Supabase using the REST API
"""

import requests
import os
import json

# Supabase configuration
SUPABASE_URL = "https://isctohcnitdotxahrdpb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlzY3RvaGNuaXRkb3R4YWhyZHBiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjQ4NjM0OSwiZXhwIjoyMDc4MDYyMzQ5fQ.7pAM_Bkw8vytUw0Ycz9tqAqNXA7RqsLtFeoqlhSFkTY"

def setup_database():
    """Setup database schema in Supabase"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    # Read schema SQL
    with open('database/schema.sql', 'r') as f:
        schema_sql = f.read()

    # Execute each statement separately using the REST API
    statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
    
    success = True
    for statement in statements:
        if not statement.strip():
            continue
            
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/",
            headers=headers,
            json={"query": statement}
        )

    if response.status_code == 200:
        print("✅ Database schema setup successful!")
        return True
    else:
        print(f"❌ Error setting up database schema: {response.text}")
        return False

if __name__ == "__main__":
    print("Setting up Supabase database schema...")
    setup_database()