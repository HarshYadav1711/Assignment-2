# 🔍 How to Check Railway Logs (CRITICAL)

## The app is crashing - we need to see WHY

The "Application failed to respond" error means the app crashed before it could start. The logs will tell us exactly why.

## Step-by-Step: View Railway Logs

### Method 1: Railway Dashboard (Easiest)

1. **Go to Railway Dashboard**: https://railway.app
2. **Click on your project**
3. **Click on your service** (the deployed app)
4. **Click "Deployments" tab** (top menu)
5. **Click on the latest deployment** (most recent one)
6. **Click "View Logs"** or scroll down to see logs
7. **Look for error messages** - they'll be in red or show stack traces

### Method 2: Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# View logs
railway logs
```

## What to Look For in Logs

### Common Errors:

1. **"Missing required environment variables"**
   ```
   ERROR: Missing required environment variables: SUPABASE_URL, SUPABASE_KEY
   ```
   **Fix**: Add missing variables in Railway → Variables tab

2. **"ModuleNotFoundError"**
   ```
   ModuleNotFoundError: No module named 'fastapi'
   ```
   **Fix**: Check requirements.txt is correct, Railway should auto-install

3. **"ValidationError"**
   ```
   pydantic_core._pydantic_core.ValidationError
   ```
   **Fix**: Check environment variable format/values

4. **"Connection refused" or "Connection error"**
   ```
   Could not connect to Supabase/OpenAI
   ```
   **Fix**: Check API keys are correct

5. **"Port already in use" or binding errors**
   ```
   Address already in use
   ```
   **Fix**: Railway handles ports automatically, shouldn't happen

## After Finding the Error

1. **Copy the error message** from logs
2. **Check which step failed**:
   - Import errors → Dependencies issue
   - Config errors → Missing env vars
   - Connection errors → Wrong API keys
3. **Fix the issue** based on the error
4. **Redeploy** (Railway auto-redeploys when you fix env vars)

## Quick Test: Check if App Starts

The logs should show:
```
INFO: Starting Conversational AI Backend...
INFO: Server will run on 0.0.0.0:XXXX
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:XXXX
```

If you DON'T see these messages, the app crashed before starting.

## Most Likely Issue

Based on the error pattern, it's **99% likely** that:
- Environment variables are missing or have placeholder values
- The app crashes when trying to load Settings()

**Check the logs** - they will show exactly which variable is missing!

## Still Can't See Logs?

1. **Try Railway CLI** (Method 2 above)
2. **Check Railway status page**: https://status.railway.app
3. **Contact Railway support** if logs aren't showing

## Next Steps

1. ✅ **Check Railway logs** (follow steps above)
2. ✅ **Find the error message**
3. ✅ **Fix the issue** (usually missing env vars)
4. ✅ **Redeploy**
5. ✅ **Test again**

The logs are your best friend - they'll tell you exactly what's wrong!

