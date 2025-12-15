# 🔧 Model Configuration Fix

## Issue
The default model `gpt-4-turbo-preview` has been deprecated by OpenAI and is no longer available.

## Solution
Updated the default model to `gpt-4o` which is the latest and most capable model.

## Available Models

You can use any of these models by setting the `OPENAI_MODEL` environment variable in your `.env` file:

### Recommended Models:
- **`gpt-4o`** (Default) - Latest, most capable model
- **`gpt-4-turbo`** - Fast and capable
- **`gpt-4`** - Standard GPT-4
- **`gpt-3.5-turbo`** - Cheaper, faster option

## How to Change the Model

### Option 1: Update `.env` file
Add this line to your `.env` file:
```env
OPENAI_MODEL=gpt-4o
```

Or use a different model:
```env
OPENAI_MODEL=gpt-3.5-turbo
```

### Option 2: Update `app/config.py`
Change the default value in the `Settings` class:
```python
openai_model: str = "gpt-3.5-turbo"  # or any other model
```

## Verify Your Model Access

To check which models you have access to:
1. Go to https://platform.openai.com/playground
2. Check the model dropdown - available models will be listed
3. Or check your API usage page to see which models you can use

## Common Issues

### "Model not found" error
- Make sure your OpenAI API key has access to the model
- Some models require specific API access levels
- Try `gpt-3.5-turbo` if you're on a free tier

### "Insufficient quota" error
- Check your OpenAI billing/usage page
- Some models have usage limits
- `gpt-3.5-turbo` is usually more accessible

## After Making Changes

1. Restart your server:
   ```bash
   # Stop the server (Ctrl+C)
   # Then restart:
   python main.py
   ```

2. Test the connection again in the frontend

