# 🚀 Vercel Deployment Guide

## ⚠️ Important Limitations

**WebSockets DO NOT work on Vercel!**

Vercel uses serverless functions which are stateless and don't support persistent WebSocket connections. Your WebSocket endpoint (`/ws/session/{session_id}`) will **not work** on Vercel.

### Alternatives for WebSocket Support:

1. **Railway** (Recommended) - Full WebSocket support
2. **Render** - WebSocket support
3. **Fly.io** - WebSocket support
4. **DigitalOcean App Platform** - WebSocket support
5. **AWS/GCP/Azure** - Full control, WebSocket support

## Current Vercel Setup

I've created the necessary files for Vercel deployment, but **WebSockets will not work**.

### Files Created:

1. **`vercel.json`** - Vercel configuration
2. **`api/index.py`** - Serverless function entry point

## Deployment Steps

### 1. Install Vercel CLI (if not already installed)

```bash
npm install -g vercel
```

### 2. Set Environment Variables in Vercel

Go to your Vercel project dashboard → Settings → Environment Variables and add:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key
HOST=0.0.0.0
PORT=8000
OPENAI_MODEL=gpt-4o
```

### 3. Deploy

```bash
vercel
```

Or push to your connected Git repository.

## What Works on Vercel

✅ REST API endpoints (`/api/*`)
✅ Health check endpoint
✅ Root endpoint
❌ WebSocket endpoints (NOT SUPPORTED)

## Recommended Deployment Options

### Option 1: Railway (Best for WebSockets)

1. Go to https://railway.app
2. Create new project
3. Connect GitHub repo
4. Add environment variables
5. Deploy - WebSockets work perfectly!

### Option 2: Render

1. Go to https://render.com
2. Create new Web Service
3. Connect GitHub repo
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables

### Option 3: Fly.io

1. Install flyctl: `curl -L https://fly.io/install.sh | sh`
2. Run: `fly launch`
3. Add secrets: `fly secrets set OPENAI_API_KEY=...`
4. Deploy: `fly deploy`

## Fixing the Current Vercel Error

The error you're seeing is likely because:

1. **Missing environment variables** - Add them in Vercel dashboard
2. **Import errors** - The serverless function can't find modules
3. **WebSocket attempt** - Trying to use WebSocket (which fails)

### Quick Fix:

1. **Add all environment variables** in Vercel dashboard
2. **Test REST endpoints only** (not WebSocket)
3. **Consider switching to Railway/Render** for full functionality

## Testing After Deployment

### Test REST Endpoints:

```bash
# Health check
curl https://your-app.vercel.app/api/health

# Root endpoint
curl https://your-app.vercel.app/
```

### WebSocket Test (Will Fail):

```javascript
// This will NOT work on Vercel
const ws = new WebSocket('wss://your-app.vercel.app/ws/session/test');
```

## Migration to Railway (Recommended)

If you need WebSocket support (which you do for this project), here's how to deploy on Railway:

1. **Sign up**: https://railway.app
2. **New Project** → Deploy from GitHub
3. **Select your repo**
4. **Add environment variables**:
   - SUPABASE_URL
   - SUPABASE_KEY
   - OPENAI_API_KEY
   - OPENAI_MODEL (optional)
5. **Railway auto-detects** Python and installs dependencies
6. **Set start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. **Deploy** - WebSockets work!

Railway provides:
- ✅ Full WebSocket support
- ✅ Persistent connections
- ✅ Free tier available
- ✅ Easy deployment
- ✅ Auto-scaling

## Summary

- **Vercel**: Works for REST APIs, NOT for WebSockets
- **Railway/Render**: Works for everything including WebSockets
- **Current error**: Likely missing env vars or WebSocket attempt
- **Solution**: Add env vars OR migrate to Railway/Render

