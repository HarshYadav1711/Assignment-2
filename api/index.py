"""
Vercel serverless function entry point.
This wraps the FastAPI app for Vercel deployment.

NOTE: WebSockets will NOT work on Vercel as it uses serverless functions.
For WebSocket support, deploy to Railway, Render, or Fly.io instead.
"""

import sys
import os

# Add parent directory to path so we can import app modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from main import app
except ImportError as e:
    # Fallback: try importing with explicit path
    import importlib.util
    main_path = os.path.join(parent_dir, 'main.py')
    spec = importlib.util.spec_from_file_location("main", main_path)
    main_module = importlib.util.module_from_spec(spec)
    sys.modules["main"] = main_module
    spec.loader.exec_module(main_module)
    app = main_module.app

# Vercel Python runtime expects 'app' to be exported
# The app is an ASGI application which Vercel can handle
__all__ = ['app']

