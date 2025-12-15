"""
OpenAI client wrapper with streaming and tool calling support.
Handles token-level streaming, function calling, and response orchestration.
"""

from typing import AsyncIterator, List, Dict, Any, Optional
import logging
from openai import AsyncOpenAI
from openai import APIError, RateLimitError, APIConnectionError, APITimeoutError
from app.config import settings
from app.llm.tools import TOOLS, execute_tool

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Production-grade LLM client with streaming and tool calling.
    
    This class orchestrates:
    - Token-level streaming responses
    - Function/tool calling detection and execution
    - Multi-turn conversation management
    - Error handling and retries
    """
    
    def __init__(self):
        """Initialize OpenAI client with API key."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def stream_response(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        session_id: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream LLM response with tool calling support.
        
        This is the core method that implements:
        1. Initial LLM call with tool definitions
        2. Tool execution if tools are requested
        3. Token-level streaming of final response
        
        Args:
            messages: Conversation history
            system_prompt: System prompt based on routing
            session_id: Session ID for logging
            
        Yields:
            Dictionary with event type and content:
            - {"type": "token", "content": "..."}
            - {"type": "tool_call", "tool": "...", "arguments": {...}}
            - {"type": "tool_result", "tool": "...", "result": {...}}
            - {"type": "done"}
        """
        # Prepare messages with system prompt
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        try:
            # First call: Check for tool usage
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                tools=TOOLS,
                tool_choice="auto",  # Let LLM decide when to use tools
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                stream=True
            )
            
            # Process streaming response
            tool_calls = []
            accumulated_content = ""
            finish_reason = None
            
            async for chunk in response:
                if not chunk.choices:
                    continue
                
                delta = chunk.choices[0].delta
                finish_reason = chunk.choices[0].finish_reason
                
                # Handle tool calls (when model decides to use tools, no content is streamed)
                if delta.tool_calls:
                    for tool_call_delta in delta.tool_calls:
                        idx = tool_call_delta.index
                        
                        # Initialize tool call if new
                        if idx >= len(tool_calls):
                            tool_calls.extend([None] * (idx + 1 - len(tool_calls)))
                        
                        if tool_calls[idx] is None:
                            tool_calls[idx] = {
                                "id": tool_call_delta.id or "",
                                "type": "function",
                                "function": {
                                    "name": "",
                                    "arguments": ""
                                }
                            }
                        
                        # Accumulate tool call data
                        if tool_call_delta.function:
                            if tool_call_delta.function.name:
                                tool_calls[idx]["function"]["name"] = tool_call_delta.function.name
                            if tool_call_delta.function.arguments:
                                tool_calls[idx]["function"]["arguments"] += tool_call_delta.function.arguments
                
                # Handle content tokens (only if no tools are being called)
                if delta.content and not tool_calls:
                    token = delta.content
                    accumulated_content += token
                    yield {
                        "type": "token",
                        "content": token
                    }
            
            # Execute tools if any were called
            if tool_calls and finish_reason == "tool_calls":
                import json
                
                # Collect all tool calls and execute them
                all_tool_calls_formatted = []
                tool_result_messages = []
                
                for tool_call in tool_calls:
                    if tool_call and tool_call["function"]["name"]:
                        tool_name = tool_call["function"]["name"]
                        try:
                            arguments = json.loads(tool_call["function"]["arguments"])
                        except json.JSONDecodeError:
                            arguments = {}
                        
                        # Yield tool call event
                        yield {
                            "type": "tool_call",
                            "tool": tool_name,
                            "arguments": arguments
                        }
                        
                        # Execute tool
                        try:
                            tool_result = await execute_tool(tool_name, arguments)
                            
                            # Yield tool result
                            yield {
                                "type": "tool_result",
                                "tool": tool_name,
                                "result": tool_result
                            }
                            
                            # Format tool result as JSON string
                            tool_result_str = json.dumps(tool_result)
                            
                            # Store for message construction
                            all_tool_calls_formatted.append({
                                "id": tool_call["id"],
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "arguments": tool_call["function"]["arguments"]
                                }
                            })
                            
                            # Store tool result message
                            tool_result_messages.append({
                                "role": "tool",
                                "content": tool_result_str,
                                "tool_call_id": tool_call["id"]
                            })
                        
                        except Exception as e:
                            logger.error(f"Tool execution error: {e}")
                            yield {
                                "type": "tool_result",
                                "tool": tool_name,
                                "result": {"error": str(e)}
                            }
                
                # Add assistant message with all tool calls, then tool results
                if all_tool_calls_formatted:
                    assistant_message = {
                        "role": "assistant",
                        "content": accumulated_content if accumulated_content else None,
                        "tool_calls": all_tool_calls_formatted
                    }
                    full_messages.append(assistant_message)
                    full_messages.extend(tool_result_messages)
                    
                    # Get final response with tool context
                    accumulated_content = ""
                    final_response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=full_messages,
                        temperature=settings.temperature,
                        max_tokens=settings.max_tokens,
                        stream=True
                    )
                    
                    async for chunk in final_response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            token = chunk.choices[0].delta.content
                            accumulated_content += token
                            yield {
                                "type": "token",
                                "content": token
                            }
            
            yield {"type": "done"}
            
        except RateLimitError as e:
            # Rate limit error (429) - too many requests per minute
            logger.error(f"Rate limit error: {e}")
            logger.error(f"Rate limit error details: status_code={getattr(e, 'status_code', None)}, response={getattr(e, 'response', None)}")
            error_message = (
                "⏱️ Rate Limit Exceeded\n\n"
                "You're making requests too quickly. Please:\n"
                "1. Wait a few seconds and try again\n"
                "2. Check your rate limits at https://platform.openai.com/account/rate-limits\n"
                "3. Consider using a model with higher rate limits (e.g., gpt-3.5-turbo)"
            )
            yield {
                "type": "error",
                "content": error_message
            }
        
        except APIError as e:
            # Handle specific OpenAI API errors
            error_code = getattr(e, 'status_code', None)
            error_response = getattr(e, 'response', None)
            
            # Try to parse error details
            error_body = {}
            error_type = ''
            error_code_str = ''
            error_message_detail = str(e)
            
            try:
                # Try multiple ways to get error details (SDK version dependent)
                if hasattr(e, 'body') and e.body:
                    if isinstance(e.body, dict):
                        error_body = e.body
                    else:
                        import json
                        error_body = json.loads(e.body) if isinstance(e.body, str) else {}
                elif error_response:
                    import json
                    if hasattr(error_response, 'json'):
                        try:
                            error_body = error_response.json() or {}
                        except:
                            error_body = {}
                    elif hasattr(error_response, 'text'):
                        try:
                            error_body = json.loads(error_response.text) if error_response.text else {}
                        except:
                            error_body = {}
                    else:
                        error_body = {}
                else:
                    error_body = {}
                
                # Extract error details
                if isinstance(error_body, dict):
                    error_info = error_body.get('error', {})
                    if isinstance(error_info, dict):
                        error_type = error_info.get('type', '')
                        error_code_str = error_info.get('code', '')
                        error_message_detail = error_info.get('message', str(e))
                    else:
                        # Sometimes error is directly in body
                        error_message_detail = error_body.get('message', str(e))
                        error_code_str = error_body.get('code', '')
                else:
                    error_message_detail = str(e)
            except Exception as parse_error:
                logger.warning(f"Could not parse error response: {parse_error}")
                error_message_detail = str(e)
            
            # Log full error details for debugging
            logger.error(f"OpenAI API error: code={error_code}, type={error_type}, code_str={error_code_str}, message={error_message_detail}")
            logger.error(f"Full error: {e}")
            
            # Check for actual quota exceeded (not rate limit)
            # Rate limit (429) with 'rate_limit_exceeded' code = too many requests per minute
            # Quota (429) with 'insufficient_quota' code = billing/quota issue
            if error_code == 429:
                if error_code_str == 'insufficient_quota':
                    error_message = (
                        "⚠️ OpenAI API Quota Exceeded\n\n"
                        "Your OpenAI API key has exceeded its usage quota. Please:\n"
                        "1. Check your billing at https://platform.openai.com/account/billing\n"
                        "2. Add payment method if needed\n"
                        "3. Wait for quota reset or upgrade your plan\n"
                        "4. Or use a different API key with available quota"
                    )
                elif error_code_str == 'rate_limit_exceeded' or (error_message_detail and 'rate_limit' in error_message_detail.lower()):
                    error_message = (
                        "⏱️ Rate Limit Exceeded\n\n"
                        "You're making requests too quickly. Please:\n"
                        "1. Wait a few seconds and try again\n"
                        "2. Check your rate limits at https://platform.openai.com/account/rate-limits\n"
                        "3. Consider using a model with higher rate limits (e.g., gpt-3.5-turbo)"
                    )
                else:
                    # Generic 429 - show both possibilities
                    error_message = (
                        "⏱️ Too Many Requests (429)\n\n"
                        f"Error: {error_message_detail}\n\n"
                        "This could be:\n"
                        "1. Rate limit (too many requests per minute) - wait and retry\n"
                        "2. Quota exceeded (billing issue) - check https://platform.openai.com/account/billing\n"
                        f"Error code: {error_code_str or 'unknown'}"
                    )
            elif error_code == 401 or 'invalid_api_key' in error_message_detail.lower():
                error_message = (
                    "⚠️ OpenAI API Quota Exceeded\n\n"
                    "Your OpenAI API key has exceeded its usage quota. Please:\n"
                    "1. Check your billing at https://platform.openai.com/account/billing\n"
                    "2. Add payment method if needed\n"
                    "3. Wait for quota reset or upgrade your plan\n"
                    "4. Or use a different API key with available quota"
                )
            elif error_code == 401 or 'invalid_api_key' in str(e).lower():
                error_message = (
                    "🔑 Invalid OpenAI API Key\n\n"
                    "Please check your OPENAI_API_KEY in the .env file.\n"
                    "Get your API key from: https://platform.openai.com/api-keys"
                )
            elif error_code == 404 or 'model_not_found' in str(e).lower():
                error_message = (
                    "🤖 Model Not Available\n\n"
                    f"The model '{settings.openai_model}' is not available. Please:\n"
                    "1. Check your .env file for OPENAI_MODEL setting\n"
                    "2. Use a valid model like: gpt-4o, gpt-3.5-turbo, or gpt-4-turbo\n"
                    "3. Verify model access at https://platform.openai.com/playground"
                )
            elif error_code == 429:
                # Generic 429 (could be rate limit or quota, but we already handled rate limit above)
                error_message = (
                    "⏱️ Too Many Requests\n\n"
                    "You've hit a rate or quota limit. Please:\n"
                    "1. Wait a moment and try again\n"
                    "2. Check your usage at https://platform.openai.com/usage\n"
                    "3. Consider using gpt-3.5-turbo for lower costs"
                )
            else:
                # Generic API error with details
                error_message = f"OpenAI API Error (Code {error_code}): {str(e)}"
            
            yield {
                "type": "error",
                "content": error_message
            }
        
        except APIConnectionError as e:
            logger.error(f"API connection error: {e}")
            error_message = (
                "🔌 Connection Error\n\n"
                "Could not connect to OpenAI API. Please:\n"
                "1. Check your internet connection\n"
                "2. Verify OpenAI API is accessible\n"
                "3. Try again in a moment"
            )
            yield {
                "type": "error",
                "content": error_message
            }
        
        except APITimeoutError as e:
            logger.error(f"API timeout error: {e}")
            error_message = (
                "⏱️ Request Timeout\n\n"
                "The request took too long. Please try again."
            )
            yield {
                "type": "error",
                "content": error_message
            }
        
        except Exception as e:
            # Catch-all for any other errors
            logger.error(f"Unexpected error: {e}")
            error_message = f"Unexpected error: {str(e)}\n\nPlease check the server logs for details."
            yield {
                "type": "error",
                "content": error_message
            }


# Global LLM client instance
llm_client = LLMClient()

