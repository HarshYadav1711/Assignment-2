# 🔧 .env File Setup Guide

## Current Status

Your `.env` file currently has placeholder values that need to be replaced with your actual credentials.

## Required Fields

### ✅ Already Correct (Optional)
- `HOST=0.0.0.0` - Server host (default is fine)
- `PORT=8000` - Server port (default is fine)

### ❌ Need to Update (Required)

#### 1. Supabase Configuration

```env
SUPABASE_URL=your_supabase_url_here          # ❌ Replace this
SUPABASE_KEY=your_supabase_anon_key_here     # ❌ Replace this
```

**How to get these:**
1. Go to https://supabase.com and sign in
2. Open your project (or create one)
3. Go to **Settings** (gear icon) → **API**
4. Copy:
   - **Project URL** → Replace `SUPABASE_URL`
   - **anon public** key → Replace `SUPABASE_KEY`

**Example:**
```env
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYxNjIzOTAyMiwiZXhwIjoxOTMxODE1MDIyfQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 2. OpenAI Configuration

```env
OPENAI_API_KEY=your_openai_api_key_here      # ❌ Replace this
```

**How to get this:**
1. Go to https://platform.openai.com/api-keys
2. Click **"Create new secret key"**
3. Copy the key (starts with `sk-`)
4. Replace `OPENAI_API_KEY` value

**Example:**
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Optional Fields (Recommended)

You can also add these to customize behavior:

```env
# Optional: Change the model (default is gpt-4o)
OPENAI_MODEL=gpt-3.5-turbo

# Optional: Adjust max tokens per response (default is 2000)
MAX_TOKENS=2000

# Optional: Adjust temperature (0.0-2.0, default is 0.7)
TEMPERATURE=0.7
```

## Complete Example .env File

Here's what a complete, working `.env` file should look like:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your_anon_key_here

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your_openai_key_here

# Optional: Use cheaper model for testing
OPENAI_MODEL=gpt-3.5-turbo

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## Validation Checklist

Before running the server, verify:

- [ ] `SUPABASE_URL` starts with `https://` and ends with `.supabase.co`
- [ ] `SUPABASE_KEY` is a long string starting with `eyJ`
- [ ] `OPENAI_API_KEY` starts with `sk-` or `sk-proj-`
- [ ] No extra spaces around the `=` sign
- [ ] No quotes around the values (unless they contain spaces)
- [ ] All placeholder text has been replaced

## Common Mistakes

### ❌ Wrong:
```env
SUPABASE_URL="https://example.supabase.co"  # Don't use quotes
SUPABASE_KEY = your_key_here                 # No spaces around =
OPENAI_API_KEY=your_openai_api_key_here      # Still placeholder
```

### ✅ Correct:
```env
SUPABASE_URL=https://example.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
```

## Testing Your Configuration

After updating your `.env` file, test it:

```bash
# Activate venv
.\venv\Scripts\Activate.ps1

# Try to start the server
python main.py
```

**If you see errors:**
- "Invalid API key" → Check your OpenAI key
- "Connection refused" → Check your Supabase URL
- "Authentication failed" → Check your Supabase key

## Security Notes

⚠️ **Important:**
- Never commit your `.env` file to git (it's already in `.gitignore`)
- Never share your API keys publicly
- Rotate keys if they're accidentally exposed
- Use different keys for development and production

## Need Help?

- **Supabase**: https://supabase.com/docs/guides/getting-started
- **OpenAI**: https://platform.openai.com/docs/guides/authentication

