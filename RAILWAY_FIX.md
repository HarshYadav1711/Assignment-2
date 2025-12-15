# 🔧 Railway Deployment Fix Guide

## Common Issues and Solutions

### Issue: "Application failed to respond"

This usually happens due to one of these reasons:

### 1. Missing Environment Variables (Most Common)

**Problem:** The app crashes on startup because required env vars are missing.

**Solution:**
1. Go to Railway dashboard → Your project → **Variables** tab
2. Add ALL these environment variables:

```
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
OPENAI_API_KEY=your_openai_api_key_here
HOST=0.0.0.0
OPENAI_MODEL=gpt-4o
```

**Important:** Do NOT set `PORT` manually - Railway sets it automatically!

### 2. Wrong Start Command

**Problem:** Railway might be using the wrong start command.

**Solution:**
1. Go to Railway dashboard → Your service → **Settings** → **Deploy**
2. Set **Start Command** to:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. Or leave it empty - Railway will use the `Procfile` or `railway.json` I created

### 3. App Crashing on Startup

**Check the logs:**
1. Go to Railway dashboard → Your service → **Deployments** tab
2. Click on the latest deployment
3. Check the **Logs** tab
4. Look for error messages

**Common errors:**
- `ModuleNotFoundError` → Dependencies not installed
- `ValidationError` → Missing environment variables
- `ConnectionError` → Can't connect to Supabase/OpenAI

### 4. Port Configuration Issue

**Problem:** App not listening on the correct port.

**Solution:** I've updated `app/config.py` to automatically read `PORT` from environment.
Railway sets `PORT` automatically, so you don't need to set it manually.

## Step-by-Step Fix

### Step 1: Check Environment Variables

1. Railway dashboard → Project → **Variables**
2. Verify these are set:
   - ✅ `SUPABASE_URL`
   - ✅ `SUPABASE_KEY`
   - ✅ `OPENAI_API_KEY`
   - ✅ `HOST=0.0.0.0`
   - ✅ `OPENAI_MODEL` (optional, defaults to gpt-4o)
   - ❌ Do NOT set `PORT` (Railway sets it)

### Step 2: Check Start Command

1. Railway dashboard → Service → **Settings** → **Deploy**
2. **Start Command** should be:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. Or leave empty to use `Procfile`/`railway.json`

### Step 3: Check Logs

1. Railway dashboard → Service → **Deployments**
2. Click latest deployment → **Logs**
3. Look for:
   - ✅ "Application startup complete"
   - ✅ "Uvicorn running on..."
   - ❌ Any error messages

### Step 4: Redeploy

After fixing environment variables:
1. Railway will auto-redeploy, OR
2. Go to **Deployments** → Click **Redeploy**

## Files I Created

1. **`Procfile`** - Tells Railway how to start the app
2. **`railway.json`** - Railway-specific configuration
3. **Updated `app/config.py`** - Now reads PORT from environment

## Testing After Fix

1. **Check health endpoint:**
   ```
   https://your-app.up.railway.app/api/health
   ```
   Should return: `{"status":"healthy",...}`

2. **Check root endpoint:**
   ```
   https://your-app.up.railway.app/
   ```
   Should return API information

3. **Test WebSocket** (if health check works):
   ```javascript
   const ws = new WebSocket('wss://your-app.up.railway.app/ws/session/test');
   ```

## Still Not Working?

### Check These:

1. **Railway Logs** - Most important! Check for specific errors
2. **Environment Variables** - All required vars must be set
3. **Start Command** - Must use `$PORT` variable
4. **Dependencies** - Check if `requirements.txt` is correct
5. **Python Version** - Railway uses Python 3.11 by default

### Get Help:

1. Copy the error from Railway logs
2. Check if it's a missing env var, import error, or connection issue
3. The logs will tell you exactly what's wrong!

## Quick Checklist

- [ ] All environment variables set in Railway
- [ ] Start command uses `$PORT`
- [ ] Checked Railway logs for errors
- [ ] Redeployed after fixing env vars
- [ ] Tested health endpoint

Most issues are solved by setting the environment variables correctly!

