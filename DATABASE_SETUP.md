# 🗄️ Database Setup Guide

This guide will help you set up the Supabase database for the Conversational AI Backend.

## Prerequisites

- A Supabase account (sign up at https://supabase.com if you don't have one)
- A Supabase project created

## Step 1: Create a Supabase Project (if you don't have one)

1. Go to https://supabase.com
2. Sign in or create an account
3. Click **"New Project"**
4. Fill in:
   - **Name**: Your project name (e.g., "conversational-ai")
   - **Database Password**: Choose a strong password (save it!)
   - **Region**: Choose closest to you
5. Click **"Create new project"**
6. Wait 2-3 minutes for the project to be provisioned

## Step 2: Get Your Supabase Credentials

1. In your Supabase project dashboard, go to **Settings** (gear icon) → **API**
2. You'll see:
   - **Project URL**: Copy this (looks like `https://xxxxx.supabase.co`)
   - **anon public key**: Copy this (long string starting with `eyJ...`)

3. Update your `.env` file with these values:
   ```env
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

## Step 3: Run the Database Schema

1. In your Supabase dashboard, click **SQL Editor** in the left sidebar
2. Click **"New query"**
3. Copy the **entire contents** of `app/db/schema.sql` file
4. Paste it into the SQL Editor
5. Click **"Run"** (or press `Ctrl+Enter`)

You should see a success message: "Success. No rows returned"

## Step 4: Verify Tables Were Created

1. In Supabase dashboard, go to **Table Editor** (left sidebar)
2. You should see two tables:
   - ✅ `sessions` - Stores session metadata
   - ✅ `session_events` - Stores event logs

3. Click on each table to verify the columns match:
   
   **sessions table:**
   - session_id (text, primary key)
   - user_id (text)
   - start_time (timestamptz)
   - end_time (timestamptz)
   - duration_seconds (integer)
   - final_summary (text)
   - created_at (timestamptz)

   **session_events table:**
   - event_id (bigint, primary key, auto-increment)
   - session_id (text, foreign key to sessions)
   - event_type (text)
   - content (text)
   - timestamp (timestamptz)
   - created_at (timestamptz)

## Step 5: Verify Indexes

1. In Supabase dashboard, go to **Database** → **Indexes**
2. You should see 4 indexes:
   - `idx_session_events_session_id`
   - `idx_session_events_timestamp`
   - `idx_sessions_user_id`
   - `idx_sessions_start_time`

## Troubleshooting

### "Permission denied" error
- Make sure you're using the **anon public key**, not the service role key
- Check that your Supabase project is active (not paused)

### "Table already exists" error
- This is fine! The schema uses `CREATE TABLE IF NOT EXISTS`
- Your tables are already set up correctly

### Can't find SQL Editor
- Make sure you're in the correct Supabase project
- SQL Editor is in the left sidebar, under "Project" section

### Tables not showing in Table Editor
- Refresh the page
- Make sure you ran the SQL successfully (check for error messages)

## Quick SQL Copy-Paste

If you want to copy the SQL directly, here it is:

```sql
-- Production-grade schema for conversational AI session management
-- Designed for high write throughput and chronological event retrieval

-- Sessions table: Core session metadata
CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    duration_seconds INTEGER,
    final_summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Session events table: Chronological event log
-- Optimized for append-heavy workloads and time-series queries
CREATE TABLE IF NOT EXISTS session_events (
    event_id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    -- event_type values: user_message, ai_token, tool_call, tool_result, system_event
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_session_events_session_id ON session_events(session_id);
CREATE INDEX IF NOT EXISTS idx_session_events_timestamp ON session_events(session_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time);
```

## Next Steps

Once your database is set up:

1. ✅ Update `.env` with your Supabase credentials
2. ✅ Update `.env` with your OpenAI API key
3. ✅ Start the server: `python main.py`
4. ✅ Test the frontend: Open `frontend/index.html`

Your database is now ready to store sessions and events!

