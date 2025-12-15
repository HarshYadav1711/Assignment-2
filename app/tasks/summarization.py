"""
Post-session AI summarization task.
Runs asynchronously after WebSocket disconnect to generate session summaries.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any
from openai import AsyncOpenAI
from app.config import settings
from app.db.client import db_client

logger = logging.getLogger(__name__)


async def generate_session_summary(session_id: str) -> None:
    """
    Generate AI-powered session summary after disconnect.
    
    This function:
    1. Loads all session events from database
    2. Constructs conversation context
    3. Uses LLM to generate insightful summary
    4. Persists summary to database
    
    This runs as a background task and does not block the server.
    
    Args:
        session_id: Session identifier to summarize
    """
    try:
        logger.info(f"Starting summarization for session {session_id}")
        
        # Load session events
        events = await db_client.get_session_events(session_id)
        
        if not events:
            logger.warning(f"No events found for session {session_id}")
            return
        
        # Construct conversation context
        conversation_text = _build_conversation_text(events)
        
        # Generate summary using LLM
        summary = await _generate_summary_with_llm(conversation_text, session_id)
        
        # Calculate session duration
        start_event = events[0]
        end_event = events[-1]
        start_time = datetime.fromisoformat(start_event["timestamp"].replace("Z", "+00:00"))
        end_time = datetime.fromisoformat(end_event["timestamp"].replace("Z", "+00:00"))
        duration_seconds = int((end_time - start_time).total_seconds())
        
        # Persist summary
        await db_client.update_session_summary(
            session_id=session_id,
            summary=summary,
            end_time=end_time,
            duration_seconds=duration_seconds
        )
        
        logger.info(f"Summarization completed for session {session_id}")
    
    except Exception as e:
        logger.error(f"Error during summarization for session {session_id}: {e}")


def _build_conversation_text(events: List[Dict[str, Any]]) -> str:
    """
    Build readable conversation text from events.
    
    Args:
        events: List of session events
        
    Returns:
        Formatted conversation text
    """
    conversation_lines = []
    
    for event in events:
        event_type = event["event_type"]
        content = event["content"]
        
        if event_type == "user_message":
            conversation_lines.append(f"User: {content}")
        elif event_type == "ai_token":
            # Accumulate tokens (simplified - in reality we'd need to group)
            pass
        elif event_type == "tool_call":
            conversation_lines.append(f"[Tool Call: {content}]")
        elif event_type == "tool_result":
            conversation_lines.append(f"[Tool Result: {content}]")
    
    return "\n".join(conversation_lines)


async def _generate_summary_with_llm(conversation_text: str, session_id: str) -> str:
    """
    Use LLM to generate session summary.
    
    Args:
        conversation_text: Full conversation text
        session_id: Session identifier
        
    Returns:
        Generated summary string
    """
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    prompt = f"""Analyze the following conversation and generate a concise but insightful summary.

Conversation:
{conversation_text}

Please provide:
1. A brief overview of the conversation
2. Key topics discussed
3. Notable user intent shifts or patterns
4. Any important insights or conclusions

Format your response as a clear, structured summary suitable for post-session review."""

    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are an expert at analyzing conversations and extracting key insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        
        return response.choices[0].message.content or "No summary generated"
    
    except Exception as e:
        logger.error(f"LLM summarization error: {e}")
        return f"Summary generation failed: {str(e)}"

