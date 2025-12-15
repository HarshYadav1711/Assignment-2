# 🚂 Railway Deployment Guide (Recommended)

Railway is the **best option** for deploying this project because it supports WebSockets, which Vercel does not.

## Why Railway?

✅ **Full WebSocket Support** - Your `/ws/session/{session_id}` endpoint will work  
✅ **Persistent Connections** - Required for real-time streaming  
✅ **Easy Deployment** - Connect GitHub and deploy  
✅ **Free Tier Available** - $5 free credit monthly  
✅ **Auto-scaling** - Handles traffic automatically  

## Step-by-Step Deployment

### 1. Sign Up for Railway

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Sign up with GitHub (recommended) or email

### 2. Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository
4. Railway will auto-detect it's a Python project

### 3. Configure Environment Variables

1. Go to your project → **Variables** tab
2. Add these environment variables:

```
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
OPENAI_API_KEY=your_openai_api_key_here
HOST=0.0.0.0
PORT=5000
OPENAI_MODEL=gpt-4o
```

**Note:** Railway sets `PORT` automatically via `$PORT` environment variable.

### 4. Configure Build Settings

Railway usually auto-detects, but verify:

1. Go to **Settings** → **Build**
2. **Build Command**: (leave empty or `pip install -r requirements.txt`)
3. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 5. Deploy

Railway will automatically:
- Install dependencies from `requirements.txt`
- Start your FastAPI app
- Provide a public URL

### 6. Get Your URL

1. Go to **Settings** → **Networking**
2. Click **"Generate Domain"** to get a public URL
3. Your app will be available at: `https://your-app.up.railway.app`

## Testing WebSocket

Once deployed, test your WebSocket endpoint:

```javascript
// Update frontend/index.html WebSocket URL to:
const wsUrl = `wss://your-app.up.railway.app/ws/session/${sessionId}?user_id=user_${Date.now()}`;
```

## Cost

- **Free Tier**: $5 credit/month
- **Hobby Plan**: $5/month for more resources
- **Pro Plan**: $20/month for production

For development/testing, the free tier is usually sufficient.

## Troubleshooting

### Build Fails

- Check that `requirements.txt` is in the root
- Verify Python version (Railway uses 3.11 by default)
- Check build logs in Railway dashboard

### App Crashes

- Check environment variables are set
- Verify all required env vars are present
- Check logs in Railway dashboard

### WebSocket Not Working

- Make sure you're using `wss://` (secure WebSocket) not `ws://`
- Check Railway logs for connection errors
- Verify the WebSocket endpoint is accessible

## Alternative: Render

If you prefer Render:

1. Go to https://render.com
2. Create **New Web Service**
3. Connect GitHub repo
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

Render also supports WebSockets and has a free tier.

## Summary

- ✅ **Railway**: Best for WebSockets, easy deployment
- ✅ **Render**: Good alternative, also supports WebSockets
- ❌ **Vercel**: Does NOT support WebSockets (serverless limitation)

For this project, **Railway is strongly recommended**.

