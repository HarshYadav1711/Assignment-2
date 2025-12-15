# 💳 OpenAI API Quota Fix Guide

## Error: "You exceeded your current quota"

This error means your OpenAI API key has reached its usage limit or doesn't have billing set up.

## Quick Fixes

### Option 1: Add Payment Method (Recommended)

1. Go to https://platform.openai.com/account/billing
2. Click **"Add payment method"**
3. Add a credit card or payment method
4. Set up usage limits if desired
5. Your quota will be restored immediately

### Option 2: Check Your Usage

1. Go to https://platform.openai.com/usage
2. Check your current usage and limits
3. See when your quota resets (if on free tier)

### Option 3: Use a Different API Key

If you have multiple OpenAI accounts or keys:

1. Get a new API key from https://platform.openai.com/api-keys
2. Update your `.env` file:
   ```env
   OPENAI_API_KEY=sk-your-new-key-here
   ```
3. Restart the server

### Option 4: Switch to a Cheaper Model

If you're on a tight budget, use `gpt-3.5-turbo` which is much cheaper:

1. Add to your `.env` file:
   ```env
   OPENAI_MODEL=gpt-3.5-turbo
   ```
2. Restart the server

## Understanding OpenAI Pricing

- **gpt-4o**: ~$2.50 per 1M input tokens, ~$10 per 1M output tokens
- **gpt-4-turbo**: ~$10 per 1M input tokens, ~$30 per 1M output tokens  
- **gpt-3.5-turbo**: ~$0.50 per 1M input tokens, ~$1.50 per 1M output tokens

**Tip:** For testing and development, `gpt-3.5-turbo` is much more cost-effective!

## Free Tier Limits

If you're on the free tier:
- You get $5 in free credits when you sign up
- Once credits are used, you need to add a payment method
- Free tier doesn't have ongoing free usage

## After Fixing

1. Restart your server:
   ```bash
   # Stop server (Ctrl+C)
   python main.py
   ```

2. Test again in the frontend

## Prevention

- Monitor usage at https://platform.openai.com/usage
- Set up usage limits in billing settings
- Use `gpt-3.5-turbo` for development/testing
- Consider implementing rate limiting in your app

## Need Help?

- OpenAI Support: https://help.openai.com
- Check error codes: https://platform.openai.com/docs/guides/error-codes

