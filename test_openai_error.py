"""
Quick test script to diagnose OpenAI API errors.
Run this to see the exact error you're getting.
"""

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

async def test_openai():
    """Test OpenAI API connection and show detailed error if any."""
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY not set or still placeholder in .env file")
        return
    
    print(f"Testing with model: {model}")
    print(f"API Key starts with: {api_key[:10]}...")
    print()
    
    client = AsyncOpenAI(api_key=api_key)
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        print("✅ Success! API is working correctly.")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print("❌ Error occurred:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print()
        
        # Try to extract detailed error info
        if hasattr(e, 'status_code'):
            print(f"Status code: {e.status_code}")
        
        if hasattr(e, 'body'):
            print(f"Error body: {e.body}")
        
        if hasattr(e, 'response'):
            print(f"Response: {e.response}")
            if hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
        
        # Check for specific error codes
        error_str = str(e).lower()
        if "429" in str(e):
            if "insufficient_quota" in error_str:
                print("\n🔍 This is a QUOTA EXCEEDED error (billing issue)")
            elif "rate_limit" in error_str:
                print("\n🔍 This is a RATE LIMIT error (too many requests)")
            else:
                print("\n🔍 This is a 429 error - check error details above")
        
        print("\n💡 Check the error details above to understand the issue")

if __name__ == "__main__":
    asyncio.run(test_openai())

