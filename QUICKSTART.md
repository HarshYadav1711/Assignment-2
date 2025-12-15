# 🚀 Quick Start Guide

Follow these steps to run the Conversational AI Backend:

## Step 1: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example (if it exists) or create manually
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
OPENAI_API_KEY=sk-your-openai-api-key-here
HOST=0.0.0.0
PORT=8000
```

**Where to get credentials:**
- **Supabase**: Go to your Supabase project → Settings → API → Copy "Project URL" and "anon public" key
- **OpenAI**: Go to https://platform.openai.com/api-keys → Create new secret key

## Step 3: Set Up Database

1. Open your Supabase project dashboard
2. Go to **SQL Editor**
3. Copy and paste the entire contents of `app/db/schema.sql`
4. Click **Run** to execute the SQL

This creates the `sessions` and `session_events` tables.

## Step 4: Run the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 5: Test the Frontend

1. Open `frontend/index.html` in your web browser
   - You can double-click the file, or
   - Use a local server: `python -m http.server 8080` (then open http://localhost:8080/frontend/index.html)

2. Click **"Start Session"** button

3. Type a message and click **Send**

4. Watch the tokens stream in real-time!

## Testing WebSocket Directly

You can also test the WebSocket endpoint using browser console:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/session/test123?user_id=user1');

ws.onopen = () => console.log('Connected!');
ws.onmessage = (e) => console.log('Received:', JSON.parse(e.data));
ws.send(JSON.stringify({message: "Hello, explain async programming"}));
```

## Verify Everything Works

1. **Health Check**: Open http://localhost:8000/api/health in browser
   - Should return: `{"status":"healthy","message":"Conversational AI backend is operational"}`

2. **Root Endpoint**: Open http://localhost:8000/
   - Should show API information

3. **WebSocket**: Use the frontend or browser console to test

## Troubleshooting

### "Module not found" errors
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

### "Invalid API key" errors
- Check your `.env` file has correct credentials
- Make sure there are no extra spaces in the `.env` file

### "Connection refused" errors
- Make sure the server is running on port 8000
- Check if another process is using port 8000

### Database errors
- Verify Supabase URL and key are correct
- Make sure you ran the SQL schema in Supabase
- Check Supabase project is active

### WebSocket connection fails
- Make sure server is running
- Check browser console for errors
- Try using `ws://127.0.0.1:8000` instead of `ws://localhost:8000`

## Next Steps

- Try asking questions that trigger tool calls: "What is Python?", "Look up async programming"
- Check Supabase dashboard to see events being logged
- Disconnect a session and wait a few seconds, then check the `sessions` table for the AI-generated summary

---

**Need help?** Check the full README.md for detailed architecture and design decisions.

