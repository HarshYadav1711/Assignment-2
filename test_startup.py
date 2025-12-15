"""
Test script to verify the app can start without errors.
Run this locally to check for import/configuration issues.
"""

import sys
import os

print("Testing application startup...")
print("=" * 50)

# Test 1: Check Python version
print(f"Python version: {sys.version}")
print()

# Test 2: Check environment variables
print("Environment variables:")
required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "OPENAI_API_KEY"]
for var in required_vars:
    value = os.getenv(var, "NOT SET")
    if value == "NOT SET":
        print(f"  ❌ {var}: NOT SET")
    elif "your_" in value.lower() or "here" in value.lower():
        print(f"  ⚠️  {var}: Set but appears to be placeholder")
    else:
        print(f"  ✅ {var}: Set")
print()

# Test 3: Try importing modules
print("Testing imports...")
try:
    from app.config import settings
    print("  ✅ app.config imported")
except Exception as e:
    print(f"  ❌ app.config failed: {e}")
    sys.exit(1)

try:
    from fastapi import FastAPI
    print("  ✅ fastapi imported")
except Exception as e:
    print(f"  ❌ fastapi failed: {e}")
    sys.exit(1)

try:
    from app.api.routes import router
    print("  ✅ app.api.routes imported")
except Exception as e:
    print(f"  ❌ app.api.routes failed: {e}")
    sys.exit(1)

try:
    from app.api.websocket import websocket_endpoint
    print("  ✅ app.api.websocket imported")
except Exception as e:
    print(f"  ❌ app.api.websocket failed: {e}")
    sys.exit(1)

print()

# Test 4: Try creating the app
print("Testing app creation...")
try:
    from main import app
    print("  ✅ FastAPI app created successfully")
    print(f"  ✅ App title: {app.title}")
except Exception as e:
    print(f"  ❌ App creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 50)
print("✅ All tests passed! App should start correctly.")
print()
print("If this works locally but fails on Railway:")
print("1. Check Railway logs for specific errors")
print("2. Verify all environment variables are set in Railway")
print("3. Check Railway start command is correct")

